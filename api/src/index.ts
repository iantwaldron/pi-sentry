import rateLimit from "@fastify/rate-limit";
import { timingSafeEqual } from "crypto";
import "dotenv/config";
import Fastify from "fastify";
import { mkdir, readdir, readFile, stat, unlink, writeFile } from "fs/promises";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const API_KEY = process.env.API_KEY;
const ADMIN_API_KEY = process.env.ADMIN_API_KEY;
const __dirname = dirname(fileURLToPath(import.meta.url));
const CAPTURES_DIR =
  process.env.CAPTURES_DIR || join(__dirname, "..", "captures");

interface CaptureBody {
  date: string;
  image: string;
}

const captureSchema = {
  body: {
    type: "object",
    required: ["date", "image"],
    properties: {
      date: { type: "string" },
      image: { type: "string", minLength: 1 },
    },
    additionalProperties: false,
  },
};

const app = Fastify({
  logger: {
    transport: {
      target: "pino-pretty",
      options: {
        colorize: true,
        translateTime: "HH:MM:ss",
        ignore: "pid,hostname",
      },
    },
  },
  trustProxy: true,
  bodyLimit: 10 * 1024 * 1024, // 10MB for base64 images
});

await app.register(rateLimit, {
  max: 60,
  timeWindow: "1 minute",
});

interface ValidationError {
  validation?: Array<{
    instancePath?: string;
    params?: {
      missingProperty?: string;
      additionalProperty?: string;
    };
    keyword?: string;
  }>;
  statusCode?: number;
  message?: string;
}

app.setErrorHandler((error, _request, reply) => {
  const err = error as ValidationError;

  if (err.validation) {
    const field =
      err.validation[0]?.instancePath?.slice(1) ||
      err.validation[0]?.params?.missingProperty;
    const keyword = err.validation[0]?.keyword;

    let message = "Invalid request";
    if (keyword === "required") {
      message = `Missing required field: ${field}`;
    } else if (keyword === "minLength") {
      message = `${field} cannot be empty`;
    } else if (keyword === "additionalProperties") {
      message = `Unknown field: ${err.validation[0]?.params?.additionalProperty}`;
    }

    return reply.status(400).send({ error: message });
  }

  return reply
    .status(err.statusCode || 500)
    .send({ error: err.message || "Internal server error" });
});

async function validateBearerToken(
  request: { headers: Record<string, string | string[] | undefined> },
  reply: { status: (code: number) => { send: (body: object) => void } },
): Promise<void> {
  const authHeader = request.headers["authorization"];

  if (!API_KEY) {
    app.log.error("API_KEY environment variable not configured");
    return reply.status(500).send({ error: "Server configuration error" });
  }

  if (!authHeader || typeof authHeader !== "string") {
    return reply.status(401).send({ error: "Authorization header required" });
  }

  if (!authHeader.startsWith("Bearer ")) {
    return reply.status(401).send({ error: "Bearer token required" });
  }

  const token = authHeader.slice(7);

  const keyOk =
    token.length === API_KEY.length &&
    timingSafeEqual(Buffer.from(token), Buffer.from(API_KEY));

  if (!keyOk) {
    return reply.status(401).send({ error: "Invalid token" });
  }
}

async function validateAdminToken(
  request: { headers: Record<string, string | string[] | undefined> },
  reply: { status: (code: number) => { send: (body: object) => void } },
): Promise<void> {
  const authHeader = request.headers["authorization"];

  if (!ADMIN_API_KEY) {
    app.log.error("ADMIN_API_KEY environment variable not configured");
    return reply.status(500).send({ error: "Server configuration error" });
  }

  if (!authHeader || typeof authHeader !== "string") {
    return reply.status(401).send({ error: "Authorization header required" });
  }

  if (!authHeader.startsWith("Bearer ")) {
    return reply.status(401).send({ error: "Bearer token required" });
  }

  const token = authHeader.slice(7);

  const keyOk =
    token.length === ADMIN_API_KEY.length &&
    timingSafeEqual(Buffer.from(token), Buffer.from(ADMIN_API_KEY));

  if (!keyOk) {
    return reply.status(401).send({ error: "Invalid token" });
  }
}

async function validateBasicAuth(
  request: { headers: Record<string, string | string[] | undefined> },
  reply: {
    status: (code: number) => { send: (body: object) => void };
    header: (name: string, value: string) => void;
  },
): Promise<void> {
  const authHeader = request.headers["authorization"];

  if (!ADMIN_API_KEY) {
    app.log.error("ADMIN_API_KEY environment variable not configured");
    return reply.status(500).send({ error: "Server configuration error" });
  }

  if (!authHeader || typeof authHeader !== "string") {
    reply.header("WWW-Authenticate", 'Basic realm="Admin"');
    return reply.status(401).send({ error: "Authentication required" });
  }

  if (!authHeader.startsWith("Basic ")) {
    reply.header("WWW-Authenticate", 'Basic realm="Admin"');
    return reply.status(401).send({ error: "Basic authentication required" });
  }

  const base64Credentials = authHeader.slice(6);
  let credentials: string;
  try {
    credentials = Buffer.from(base64Credentials, "base64").toString("utf-8");
  } catch {
    reply.header("WWW-Authenticate", 'Basic realm="Admin"');
    return reply.status(401).send({ error: "Invalid credentials format" });
  }

  const [, password] = credentials.split(":");

  if (!password) {
    reply.header("WWW-Authenticate", 'Basic realm="Admin"');
    return reply.status(401).send({ error: "Password required" });
  }

  const keyOk =
    password.length === ADMIN_API_KEY.length &&
    timingSafeEqual(Buffer.from(password), Buffer.from(ADMIN_API_KEY));

  if (!keyOk) {
    reply.header("WWW-Authenticate", 'Basic realm="Admin"');
    return reply.status(401).send({ error: "Invalid credentials" });
  }
}

function generateFilename(): string {
  const now = new Date();
  const pad = (n: number) => n.toString().padStart(2, "0");
  const month = pad(now.getMonth() + 1);
  const day = pad(now.getDate());
  const year = now.getFullYear();
  const hours = pad(now.getHours());
  const minutes = pad(now.getMinutes());
  const seconds = pad(now.getSeconds());
  return `img_${month}${day}${year}${hours}${minutes}${seconds}.png`;
}

app.get("/health", async () => {
  return { status: "ok" };
});

app.post<{ Body: CaptureBody }>(
  "/capture",
  { schema: captureSchema, preHandler: validateBearerToken },
  async (request, reply) => {
    const { date, image } = request.body;

    const filename = generateFilename();
    const filePath = join(CAPTURES_DIR, filename);

    app.log.info({ date, imageSize: image.length, filename }, "Saving capture");

    try {
      await mkdir(CAPTURES_DIR, { recursive: true });
      const imageBuffer = Buffer.from(image, "base64");
      await writeFile(filePath, imageBuffer);

      app.log.info({ filename }, "Capture saved");

      return reply.status(201).send({
        success: true,
        message: "Capture saved",
        filename,
        date,
      });
    } catch (err) {
      const error = err as Error;
      app.log.error(
        { error: error.message, filename },
        "Failed to save capture",
      );
      return reply.status(500).send({ error: "Failed to save image" });
    }
  },
);

app.get(
  "/admin/captures",
  { preHandler: validateAdminToken },
  async (_request, reply) => {
    try {
      await mkdir(CAPTURES_DIR, { recursive: true });
      const files = await readdir(CAPTURES_DIR);

      const captures = await Promise.all(
        files
          .filter((f) => f.endsWith(".png"))
          .map(async (filename) => {
            const filePath = join(CAPTURES_DIR, filename);
            const [stats, fileBuffer] = await Promise.all([
              stat(filePath),
              readFile(filePath),
            ]);
            const base64 = fileBuffer.toString("base64");
            return {
              filename,
              size: stats.size,
              createdAt: stats.birthtime.toISOString(),
              url: `data:image/png;base64,${base64}`,
            };
          }),
      );

      captures.sort(
        (a, b) =>
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
      );

      return reply.send({
        captures,
        count: captures.length,
      });
    } catch (err) {
      const error = err as Error;
      app.log.error({ error: error.message }, "Failed to list captures");
      return reply.status(500).send({ error: "Failed to list captures" });
    }
  },
);

app.delete<{ Params: { filename: string } }>(
  "/admin/captures/:filename",
  { preHandler: validateBasicAuth },
  async (request, reply) => {
    const { filename } = request.params;

    // Validate filename to prevent path traversal
    if (
      !filename ||
      filename.includes("/") ||
      filename.includes("\\") ||
      filename.includes("..")
    ) {
      return reply.status(400).send({ error: "Invalid filename" });
    }

    if (!filename.endsWith(".png")) {
      return reply.status(400).send({ error: "Only PNG files can be deleted" });
    }

    const filePath = join(CAPTURES_DIR, filename);

    try {
      await stat(filePath);
    } catch {
      return reply.status(404).send({ error: "File not found" });
    }

    try {
      await unlink(filePath);
      app.log.info({ filename }, "Capture deleted");
      return reply.send({
        success: true,
        message: "Capture deleted",
        filename,
      });
    } catch (err) {
      const error = err as Error;
      app.log.error(
        { error: error.message, filename },
        "Failed to delete capture",
      );
      return reply.status(500).send({ error: "Failed to delete capture" });
    }
  },
);

app.get(
  "/admin/viewer",
  { preHandler: validateBasicAuth },
  async (_request, reply) => {
    try {
      await mkdir(CAPTURES_DIR, { recursive: true });
      const files = await readdir(CAPTURES_DIR);

      const captures = await Promise.all(
        files
          .filter((f) => f.endsWith(".png"))
          .map(async (filename) => {
            const filePath = join(CAPTURES_DIR, filename);
            const [stats, fileBuffer] = await Promise.all([
              stat(filePath),
              readFile(filePath),
            ]);
            const base64 = fileBuffer.toString("base64");
            return {
              filename,
              size: stats.size,
              createdAt: stats.birthtime.toISOString(),
              url: `data:image/png;base64,${base64}`,
            };
          }),
      );

      captures.sort(
        (a, b) =>
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
      );

      const formatBytes = (bytes: number) => {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / (1024 * 1024)).toFixed(1) + " MB";
      };

      const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Captures Viewer</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #1a1a2e;
      color: #eee;
      min-height: 100vh;
      padding: 2rem;
    }
    header {
      max-width: 1400px;
      margin: 0 auto 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    h1 { font-size: 1.5rem; color: #fff; }
    .count { color: #888; font-size: 0.9rem; }
    .grid {
      max-width: 1400px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.5rem;
    }
    .card {
      background: #16213e;
      border-radius: 12px;
      overflow: hidden;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .card:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    }
    .card img {
      width: 100%;
      height: 200px;
      object-fit: cover;
      cursor: pointer;
      background: #0f0f23;
    }
    .card-info {
      padding: 1rem;
    }
    .filename {
      font-size: 0.85rem;
      color: #fff;
      word-break: break-all;
      margin-bottom: 0.5rem;
    }
    .meta {
      display: flex;
      justify-content: space-between;
      font-size: 0.75rem;
      color: #888;
    }
    .card-actions {
      padding: 0 1rem 1rem;
    }
    .delete-btn {
      width: 100%;
      padding: 0.5rem;
      background: #dc3545;
      color: #fff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
      transition: background 0.2s;
    }
    .delete-btn:hover { background: #c82333; }
    .delete-btn:disabled {
      background: #666;
      cursor: not-allowed;
    }
    .empty {
      text-align: center;
      color: #666;
      padding: 4rem;
      grid-column: 1 / -1;
    }
    .modal {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.9);
      z-index: 1000;
      justify-content: center;
      align-items: center;
      padding: 2rem;
    }
    .modal.active { display: flex; }
    .modal img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
    .modal-close {
      position: fixed;
      top: 1rem;
      right: 1rem;
      background: none;
      border: none;
      color: #fff;
      font-size: 2rem;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <header>
    <h1>Captures Viewer</h1>
    <span class="count">${captures.length} capture${captures.length !== 1 ? "s" : ""}</span>
  </header>
  <div class="grid">
    ${
      captures.length === 0
        ? '<div class="empty">No captures yet</div>'
        : captures
            .map(
              (c) => `
      <div class="card" data-filename="${c.filename}">
        <img src="${c.url}" alt="${c.filename}" onclick="openModal(this.src)">
        <div class="card-info">
          <div class="filename">${c.filename}</div>
          <div class="meta">
            <span>${formatBytes(c.size)}</span>
            <span>${new Date(c.createdAt).toLocaleString()}</span>
          </div>
        </div>
        <div class="card-actions">
          <button class="delete-btn" onclick="deleteCapture('${c.filename}', this)">Delete</button>
        </div>
      </div>
    `,
            )
            .join("")
    }
  </div>
  <div class="modal" onclick="closeModal()">
    <button class="modal-close" onclick="closeModal()">&times;</button>
    <img src="" alt="Full size">
  </div>
  <script>
    const modal = document.querySelector('.modal');
    const modalImg = modal.querySelector('img');
    function openModal(src) {
      modalImg.src = src;
      modal.classList.add('active');
    }
    function closeModal() {
      modal.classList.remove('active');
    }
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeModal();
    });
    async function deleteCapture(filename, btn) {
      if (!confirm('Are you sure you want to delete this capture?')) return;
      btn.disabled = true;
      btn.textContent = 'Deleting...';
      try {
        const res = await fetch('/admin/captures/' + encodeURIComponent(filename), { method: 'DELETE' });
        if (res.ok) {
          const card = btn.closest('.card');
          card.style.transition = 'opacity 0.3s, transform 0.3s';
          card.style.opacity = '0';
          card.style.transform = 'scale(0.9)';
          setTimeout(() => {
            card.remove();
            const count = document.querySelectorAll('.card').length;
            document.querySelector('.count').textContent = count + ' capture' + (count !== 1 ? 's' : '');
            if (count === 0) {
              document.querySelector('.grid').innerHTML = '<div class="empty">No captures yet</div>';
            }
          }, 300);
        } else {
          const data = await res.json();
          alert('Failed to delete: ' + (data.error || 'Unknown error'));
          btn.disabled = false;
          btn.textContent = 'Delete';
        }
      } catch (err) {
        alert('Failed to delete: ' + err.message);
        btn.disabled = false;
        btn.textContent = 'Delete';
      }
    }
  </script>
</body>
</html>`;

      return reply.type("text/html").send(html);
    } catch (err) {
      const error = err as Error;
      app.log.error({ error: error.message }, "Failed to render viewer");
      return reply.status(500).send({ error: "Failed to render viewer" });
    }
  },
);

const PORT = parseInt("3050", 10);

try {
  await app.listen({ port: PORT, host: "0.0.0.0" });
  console.log(`Server listening on port ${PORT}`);
} catch (err) {
  app.log.error(err);
  process.exit(1);
}

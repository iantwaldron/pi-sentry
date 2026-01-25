import rateLimit from "@fastify/rate-limit";
import { timingSafeEqual } from "crypto";
import "dotenv/config";
import Fastify from "fastify";
import { mkdir, readdir, readFile, stat, writeFile } from "fs/promises";
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

const PORT = parseInt("3050", 10);

try {
  await app.listen({ port: PORT, host: "0.0.0.0" });
  console.log(`Server listening on port ${PORT}`);
} catch (err) {
  app.log.error(err);
  process.exit(1);
}

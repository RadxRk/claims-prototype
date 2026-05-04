import sharp from "sharp";

const MAX_DIMENSION = 2576; // Opus 4.7's max long-edge
const TARGET_FORMAT = "jpeg";

export interface PreprocessResult {
  buffer: Buffer;
  filename: string;
  mimeType: string;
  originalBytes: number;
  processedBytes: number;
  width: number;
  height: number;
}

/**
 * Resize to fit Claude's vision input ceiling, strip EXIF (PII removal —
 * GPS coordinates, timestamps, device info), normalize to JPEG.
 */
export async function preprocessImage(input: Buffer, filename = "upload.jpg"): Promise<PreprocessResult> {
  const originalBytes = input.byteLength;

  const pipeline = sharp(input, { failOn: "error" })
    .rotate() // honor EXIF orientation BEFORE stripping EXIF
    .resize({ width: MAX_DIMENSION, height: MAX_DIMENSION, fit: "inside", withoutEnlargement: true })
    .jpeg({ quality: 90, mozjpeg: true });

  const { data, info } = await pipeline.toBuffer({ resolveWithObject: true });

  return {
    buffer: data,
    filename: filename.replace(/\.[^.]+$/, ".jpg"),
    mimeType: `image/${TARGET_FORMAT}`,
    originalBytes,
    processedBytes: data.byteLength,
    width: info.width,
    height: info.height,
  };
}


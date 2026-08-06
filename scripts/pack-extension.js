import fs from "fs";
import path from "path";
import JSZip from "jszip";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");
const distDir = path.resolve(rootDir, "dist");
const zipPath = path.resolve(distDir, "extension.zip");

function getFilesRecursively(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat.isDirectory()) {
      getFilesRecursively(filePath, fileList);
    } else {
      // Do not include an existing zip file inside the zip itself
      if (filePath !== zipPath) {
        fileList.push(filePath);
      }
    }
  }
  return fileList;
}

async function main() {
  console.log("📦 Starting Chrome Extension packaging...");
  
  if (!fs.existsSync(distDir)) {
    console.error("❌ Error: dist folder does not exist. Run 'npm run build' first.");
    process.exit(1);
  }

  const zip = new JSZip();
  const files = getFilesRecursively(distDir);

  for (const file of files) {
    const relativePath = path.relative(distDir, file);
    const fileData = fs.readFileSync(file);
    zip.file(relativePath, fileData);
    console.log(`  + Adding: ${relativePath}`);
  }

  try {
    const content = await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
    fs.writeFileSync(zipPath, content);
    console.log(`\n✨ Successfully created Chrome Extension ZIP in dist: ${zipPath}`);

    // Also write to public folder so it's available in Vite dev preview mode
    const publicZipPath = path.resolve(rootDir, "public", "extension.zip");
    fs.writeFileSync(publicZipPath, content);
    console.log(`✨ Successfully mirrored Chrome Extension ZIP to public: ${publicZipPath}`);
    console.log(`📊 Size: ${(content.length / 1024 / 1024).toFixed(2)} MB\n`);
  } catch (error) {
    console.error("❌ Failed to generate ZIP file:", error);
    process.exit(1);
  }
}

main();

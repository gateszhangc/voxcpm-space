const http = require("http");
const fs = require("fs");
const path = require("path");

const host = process.env.HOSTNAME || "0.0.0.0";
const port = Number(process.env.PORT || 3000);
const root = __dirname;

const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".manifest": "application/manifest+json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".ttf": "font/ttf",
  ".txt": "text/plain; charset=utf-8",
  ".webmanifest": "application/manifest+json; charset=utf-8",
  ".xml": "application/xml; charset=utf-8"
};

const send = (response, statusCode, headers, body) => {
  response.writeHead(statusCode, headers);
  response.end(body);
};

const resolveRequestPath = (pathname) => {
  if (pathname === "/") {
    return "/index.html";
  }

  if (pathname.endsWith("/")) {
    return `${pathname}index.html`;
  }

  if (!path.extname(pathname)) {
    return `${pathname}/index.html`;
  }

  return pathname;
};

const serveFile = (requestPath, response) => {
  const safePath = path.normalize(requestPath).replace(/^(\.\.[/\\])+/, "");
  const resolvedPath = path.join(root, safePath);

  if (!resolvedPath.startsWith(root)) {
    send(response, 403, { "Content-Type": "text/plain; charset=utf-8" }, "Forbidden");
    return;
  }

  fs.readFile(resolvedPath, (error, body) => {
    if (error) {
      if (error.code === "ENOENT") {
        send(response, 404, { "Content-Type": "text/plain; charset=utf-8" }, "Not Found");
        return;
      }

      send(response, 500, { "Content-Type": "text/plain; charset=utf-8" }, "Internal Server Error");
      return;
    }

    const ext = path.extname(resolvedPath).toLowerCase();
    const cacheControl = ext === ".html" ? "no-cache" : "public, max-age=31536000, immutable";

    send(
      response,
      200,
      {
        "Cache-Control": cacheControl,
        "Content-Type": contentTypes[ext] || "application/octet-stream",
        "X-Content-Type-Options": "nosniff"
      },
      body
    );
  });
};

const server = http.createServer((request, response) => {
  const url = new URL(request.url || "/", `http://${request.headers.host || "localhost"}`);
  const pathname = decodeURIComponent(url.pathname);

  if (pathname === "/healthz") {
    send(response, 200, { "Content-Type": "application/json; charset=utf-8" }, JSON.stringify({ ok: true }));
    return;
  }

  serveFile(resolveRequestPath(pathname), response);
});

server.listen(port, host, () => {
  console.log(`Static site listening on http://${host}:${port}`);
});

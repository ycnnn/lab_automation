const express = require("express");
const http = require("http");
const socketIo = require("socket.io");
const fs = require("fs");

// Initialize server
const app = express();
const server = http.createServer(app);
const io = socketIo(server);

const PORT = 3000; // Change this if needed
const LOCAL_FILE = "text-data.txt";

// Serve static files
app.use(express.static("public"));

// Handle text file reading
let currentText = "";
if (fs.existsSync(LOCAL_FILE)) {
  currentText = fs.readFileSync(LOCAL_FILE, "utf8");
}

// WebSocket connection
io.on("connection", (socket) => {
  console.log("New client connected");

  // Send current text to newly connected client
  socket.emit("update-text", currentText);

  // Listen for text updates
  socket.on("edit-text", (newText) => {
    currentText = newText;
    fs.writeFileSync(LOCAL_FILE, currentText); // Save to file
    io.emit("update-text", currentText); // Broadcast to all clients
  });

  socket.on("disconnect", () => {
    console.log("Client disconnected");
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

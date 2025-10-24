import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./App.css"; // ✅ make sure CSS is globally applied

const container = document.getElementById("root");

// ✅ React 18 standard rendering
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ImageDetect from "./pages/ImageDetect";
import VideoDetect from "./pages/VideoDetect";
import AudioDetect from "./pages/AudioDetect";
import TextDetect from "./pages/TextDetect";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/detect/image" element={<ImageDetect />} />
          <Route path="/detect/video" element={<VideoDetect />} />
          <Route path="/detect/audio" element={<AudioDetect />} />
          <Route path="/detect/text" element={<TextDetect />} />
        </Routes>
      </main>
      <footer className="text-center text-xs text-white/40 py-6">
        © {new Date().getFullYear()} DeepGuard — assistive evidence, not legal proof.
      </footer>
    </div>
  );
}

import { Link, NavLink } from "react-router-dom";
import { ShieldCheck, LogOut, User } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const navItem = ({ isActive }) =>
  `px-3 py-2 rounded-md text-sm transition ${isActive ? "text-white bg-white/10" : "text-white/70 hover:text-white"}`;

export default function Navbar() {
  const { user, logout } = useAuth();
  return (
    <header className="border-b border-white/10 bg-black/30 backdrop-blur sticky top-0 z-30">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-semibold text-white">
          <ShieldCheck className="text-indigo-400" />
          DeepGuard
        </Link>
        <nav className="flex items-center gap-1">
          <NavLink to="/" end className={navItem}>Home</NavLink>
          <NavLink to="/detect/image" className={navItem}>Image</NavLink>
          <NavLink to="/detect/video" className={navItem}>Video</NavLink>
          <NavLink to="/detect/audio" className={navItem}>Audio</NavLink>
          <NavLink to="/detect/text" className={navItem}>Text</NavLink>
          <NavLink to="/about" className={navItem}>About</NavLink>
          <NavLink to="/contact" className={navItem}>Contact</NavLink>
          {user ? (
            <>
              <NavLink to="/dashboard" className={navItem}>Dashboard</NavLink>
              <button onClick={logout} className="btn-ghost ml-2"><LogOut size={16} /> Logout</button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={navItem}>Login</NavLink>
              <NavLink to="/register" className="btn-primary ml-2"><User size={16} /> Sign up</NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

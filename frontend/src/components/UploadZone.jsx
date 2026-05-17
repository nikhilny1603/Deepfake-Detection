import { useDropzone } from "react-dropzone";
import { UploadCloud } from "lucide-react";

export default function UploadZone({ accept, onFile, file }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept,
    multiple: false,
    onDrop: (files) => files[0] && onFile(files[0]),
  });
  return (
    <div
      {...getRootProps()}
      className={`glass p-10 text-center cursor-pointer transition border-2 border-dashed
        ${isDragActive ? "border-indigo-400 bg-indigo-500/10" : "border-white/10 hover:border-white/30"}`}
    >
      <input {...getInputProps()} />
      <UploadCloud className="mx-auto mb-3 text-indigo-300" size={36} />
      <p className="text-white/80">
        {file ? <span className="font-medium">{file.name}</span> : "Drag & drop a file here, or click to browse"}
      </p>
      <p className="text-xs text-white/40 mt-1">Max ~50MB. We never share your files.</p>
    </div>
  );
}

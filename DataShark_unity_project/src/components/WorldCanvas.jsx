"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";

function PlaceholderWorld({ theme }) {
  return (
    <mesh rotation={[0.4, 0.4, 0]}>
      <boxGeometry args={[2.5, 2.5, 2.5]} />
      <meshStandardMaterial color={theme === "ciencia ficción" ? "#38bdf8" : "#f59e0b"} />
    </mesh>
  );
}

export default function WorldCanvas({ theme }) {
  return (
    <div className="canvas-container">
      <Canvas camera={{ position: [3, 3, 3], fov: 55 }}>
        <color attach="background" args={["#050816"]} />
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 5, 5]} intensity={1.2} />
        <PlaceholderWorld theme={theme} />
        <OrbitControls enablePan={false} />
        <Environment preset="city" />
      </Canvas>
    </div>
  );
}

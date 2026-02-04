import "./globals.css";

export const metadata = {
  title: "DataShark",
  description: "Generación de juegos 3D desde texto en la web"
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}

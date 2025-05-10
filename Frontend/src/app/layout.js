import './globals.css';
import { Jost, Laila } from 'next/font/google';

// Note: Kyiv Type Sans might not be available in Google Fonts API directly
// You may need to host it yourself or use a different approach for this font

const jost = Jost({
  subsets: ['latin'],
  variable: '--font-jost',
  display: 'swap',
  weight: ['400', '500', '600', '700'],
});

const laila = Laila({
  subsets: ['latin'],
  variable: '--font-laila',
  display: 'swap',
  weight: ['300', '400', '500', '600', '700'],
});

export const metadata = {
  title: 'AI-Driven Compliance for Islamic Finance',
  description: 'Simplifying AAOIFI standards adoption for Islamic finance',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
      </head>
      <body className={`${jost.variable} ${laila.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
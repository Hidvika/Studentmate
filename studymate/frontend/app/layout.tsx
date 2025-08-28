import { ReactNode } from 'react';
import './globals.css';

export const metadata = {
  title: 'StudyMate',
  description: 'RAG UI for StudyMate',
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>{children}
        
      </body>
    </html>
  );
}
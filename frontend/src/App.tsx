import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function App() {
  return (
    <div className="min-h-screen grid place-items-center">
      <Card className="p-6 space-y-4">
        <h1 className="text-2xl font-semibold">FitDojo UI Check</h1>
        <Button>Primary Button</Button>
        <Button variant="secondary">Secondary Button</Button>
      </Card>
    </div>
  );
}



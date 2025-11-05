import { Button } from "../components/ui/button";
import { useAuth } from "../hooks/useAuth";


export default function Dashboard() {
  const { logout } = useAuth();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold">Welcome to FitDojo 🥋</h1>
      <p className="text-muted-foreground mt-2">You’re logged in!</p>
      <Button onClick={logout}>Logout</Button>
    </div>
  );
}

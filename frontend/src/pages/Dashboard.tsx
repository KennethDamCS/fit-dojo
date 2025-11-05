// src/pages/Dashboard.tsx
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/card";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/use-toast";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const { toast } = useToast();

  const handleLogout = async () => {
    try {
      await logout();
      toast({
        title: "Logged out",
        description: "See you next time 👋",
      });
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (err) {
      // Just in case logout throws
      toast({
        variant: "destructive",
        title: "Logout failed",
        description: "Please try again in a moment.",
      });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">FitDojo 🥋</h1>
            <p className="text-sm text-muted-foreground">
              Train smarter. Track better.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {user && (
              <span className="text-sm text-muted-foreground">
                Signed in as <span className="font-medium">{user.email}</span>
              </span>
            )}
            <Button variant="outline" size="sm" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-5xl flex-col gap-6 px-6 py-6">
        <div className="flex flex-col gap-4 md:flex-row">
          {/* Left: TDEE / overview */}
          <Card className="flex-1">
            <CardHeader>
              <CardTitle>Dashboard</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Welcome back{user ? `, ${user.email}` : ""}.
              </p>

              <div className="rounded-xl border bg-muted/40 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  TDEE / Goals (coming soon)
                </p>
                <p className="mt-1 text-sm">
                  We’ll show your estimated TDEE, goal calories, and weekly
                  trend here once the calculator is wired up.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Right: Account / navigation */}
          <Card className="w-full md:w-80">
            <CardHeader>
              <CardTitle>Account</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {user && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Email</span>
                    <span className="font-medium truncate max-w-[160px] text-right">
                      {user.email}
                    </span>
                  </div>
                </>
              )}

              <div className="pt-2">
                <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Security
                </p>
                <Button asChild variant="outline" size="sm" className="w-full">
                  <Link to="/profile/sessions">View active sessions</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

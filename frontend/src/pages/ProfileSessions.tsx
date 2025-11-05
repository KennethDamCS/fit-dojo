
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { useToast } from "../hooks/use-toast";
import { getSessions, revokeAllSessions, type Session } from "../lib/auth";
import { useAuth } from "../hooks/useAuth";

export default function ProfileSessions() {
  const [sessions, setSessions] = useState<Session[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [revoking, setRevoking] = useState(false);
  const { toast } = useToast();
  const { user } = useAuth();

  useEffect(() => {
    let cancelled = false;

    const fetchSessions = async () => {
      try {
        const data = await getSessions();
        if (!cancelled) {
          setSessions(data);
        }
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (err: unknown) {
        if (!cancelled) {
          toast({
            variant: "destructive",
            title: "Could not load sessions",
            description: "Please refresh the page and try again.",
          });
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchSessions();
    return () => {
      cancelled = true;
    };
  }, [toast]);

  const handleRevokeAll = async () => {
    setRevoking(true);
    try {
      await revokeAllSessions();

      toast({
        title: "Sessions revoked",
        description:
          "All devices have been logged out. You’ll stay signed in here.",
      });

      // Re-fetch sessions to reflect new state
      const data = await getSessions();
      setSessions(data);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (err: unknown) {
      toast({
        variant: "destructive",
        title: "Failed to revoke sessions",
        description: "Please try again in a moment.",
      });
    } finally {
      setRevoking(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">
              Account Sessions
            </h1>
            <p className="text-sm text-muted-foreground">
              Manage where your FitDojo account is signed in.
            </p>
            {user && (
              <p className="mt-1 text-xs text-muted-foreground">
                Signed in as <span className="font-medium">{user.email}</span>
              </p>
            )}
          </div>

          <Button variant="outline" size="sm" asChild>
            <Link to="/">Back to dashboard</Link>
          </Button>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <div>
              <CardTitle>Active sessions</CardTitle>
              <p className="mt-1 text-sm text-muted-foreground">
                These are devices currently signed in to your account.
              </p>
            </div>
            <Button
              variant="destructive"
              size="sm"
              onClick={handleRevokeAll}
              disabled={revoking || loading || !sessions?.length}
            >
              {revoking ? "Revoking..." : "Revoke all"}
            </Button>
          </CardHeader>
          <CardContent>
            {loading && (
              <p className="text-sm text-muted-foreground">
                Loading sessions…
              </p>
            )}

            {!loading && (!sessions || sessions.length === 0) && (
              <p className="text-sm text-muted-foreground">
                No active sessions found.
              </p>
            )}

            {!loading && sessions && sessions.length > 0 && (
              <div className="mt-2 space-y-2">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex flex-col gap-1 rounded-lg border bg-muted/40 p-3 text-sm md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">
                          {session.is_current ? "This device" : "Other device"}
                        </span>
                        {session.is_current && (
                          <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-xs font-medium text-emerald-600">
                            current
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {session.user_agent || "Unknown device"}
                      </p>
                    </div>

                    <div className="mt-2 text-xs text-muted-foreground md:mt-0 md:text-right">
                      {session.ip_address && <p>IP: {session.ip_address}</p>}
                      {session.created_at && (
                        <p>
                          Signed in:{" "}
                          {new Date(session.created_at).toLocaleString()}
                        </p>
                      )}
                      {session.last_seen_at && (
                        <p>
                          Last seen:{" "}
                          {new Date(session.last_seen_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

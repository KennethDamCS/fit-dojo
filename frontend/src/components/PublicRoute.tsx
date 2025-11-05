import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function PublicRoute(){
    const { user, loading } = useAuth();
    if (loading) return <div>Loading...</div>;
    return user ? <Navigate to="/" /> : <Outlet />;
}
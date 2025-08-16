import { RouterProvider } from "react-router-dom";
import { router } from "./layouts/RoutesConfig.tsx";

function App() {
    return <RouterProvider router={ router } />;
}
export default App;

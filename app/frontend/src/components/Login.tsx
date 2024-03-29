import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { StatusMessageContext } from "../App";

// TODO: 로그임 하면 유저 이름을 보여주는 메인 페이지로 이동 "{userId}과 달은 연예인..."

const Login = () => {
  const [userId, setuserId] = useState("");
  const [userPw, setuserPw] = useState("");

  const { setIsLoggedIn } = useAuth();

  const { setStatusMessage } = useContext(StatusMessageContext);

  const navigate = useNavigate();

  const handleLogin = async () => {
    // try {
    // Example: API call for user authentication
    fetch("/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ userId, userPw }),
    })
      .then((response) => response.json()) // Extract JSON data from response
      .then((data) => {
        setStatusMessage(data.message); // Pass the JSON data to setStatusMessage
        // console.log(data.message);
        setIsLoggedIn(true);
        navigate("/profile");
      })
      .catch((error) => console.log("Error:", error));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    // Here, you'd typically send the email and userPw to the backend for verification
    console.log("Login credentials", { userId, userPw });
    // send the email and userPw to the backend
    handleLogin();
  };

  return (
    <>
      <form onSubmit={handleSubmit}>
        <h2>Login</h2>
        <div>
          <label>userId: </label>
          <input
            type="text"
            value={userId}
            onChange={(e) => setuserId(e.target.value)}
            required
          />
        </div>
        <div>
          <label>userPw: </label>
          <input
            type="password"
            value={userPw}
            onChange={(e) => setuserPw(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>
      <button onClick={() => navigate("/signup")}>Signup</button>
    </>
  );
};

export default Login;

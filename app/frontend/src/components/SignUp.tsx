import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { StatusMessageContext } from "../App";

const Signup = () => {
  const [userId, setUserId] = useState("");
  const [username, setUsername] = useState("");
  const [userPw, setUserPw] = useState("");
  const [checkPw, setCheckPw] = useState("");
  const [gender, setGender] = useState("");

  const navigate = useNavigate();

  const { setStatusMessage } = useContext(StatusMessageContext);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    // Here, you'd typically send the email and userPw to the backend to register the new user
    console.log("Signup details", { userId, userPw, gender });

    // send the email and userPw to the backend
    fetch("/api/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId, userPw, checkPw, username, gender }),
    })
      .then((response) => response.json()) // Extract JSON data from response
      .then((data) => {
        setStatusMessage(data.message); // Pass the JSON data to setStatusMessage
        // console.log(data.message);
        navigate("/");
      })
      .catch((error) => console.log("Error:", error));
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Signup</h2>
      <div>
        <label>userId: </label>
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          required
        />
      </div>
      <div>
        <label>username: </label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>
      <div>
        <label>userPw: </label>
        <input
          type="password"
          value={userPw}
          onChange={(e) => setUserPw(e.target.value)}
          required
        />
      </div>
      <div>
        <label>checkPW: </label>
        <input
          type="password"
          value={checkPw}
          onChange={(e) => setCheckPw(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Gender: </label>
        <select value={gender} onChange={(e) => setGender(e.target.value)}>
          <option value={"Male"}>male</option>
          <option value={"Female"}>female</option>
        </select>
      </div>
      <button type="submit">Signup</button>
    </form>
  );
};

export default Signup;

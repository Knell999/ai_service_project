import { useState } from 'react';

const Signup = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [gender, setGender] = useState('');

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    // Here, you'd typically send the email and password to the backend to register the new user
    console.log('Signup details', { username, password, gender });

    // send the email and password to the backend
    fetch('/api/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, gender }),
    })
      .then((response) => response.json())
      .then((data) => console.log(data))
      .catch((error) => console.log('Error:', error));
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Signup</h2>
      <div>
        <label>Username: </label>
        <input
          type="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Password: </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Gender: </label>
        <select
            value={gender}
            onChange={(e) => setGender(e.target.value)}
        >
            <option value={"Male"}>male</option>
            <option value={"Female"}>female</option>
        </select>

      </div>
      <button type="submit">Signup</button>
    </form>
  );
};

export default Signup;

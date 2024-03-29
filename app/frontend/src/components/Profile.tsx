// Assuming you have a User type defined somewhere
// type User = {
//   id: string;
//   username: string;
// };
// import { User } from '../types/User';

const Profile = () => {
  // Get the user object from the context
  const user = {
    id: "aidi",
    username: "johndoe",
  };
  // Method to handle account deletion
  const handleDelete = () => {
    // Call the onDeleteAccount method from props
    // to delete the account
    // onDeleteAccount(user.id);
    // Call the onLogout method from props
    // to log out the user
    // onLogout();
  };

  return (
    <div>
      <h2>Profile</h2>
      {/* Display user information */}
      <p>Name: {user.id}</p>
      <p>Email: {user.username}</p>
      {/* Add more user fields as needed */}

      {/* Delete account button */}
      <button onClick={handleDelete}>Delete Account</button>
    </div>
  );
};

export default Profile;

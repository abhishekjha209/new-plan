// Add a basic React component that returns a dummy login form.
const LoginPage = () => {
    return (
        <div>
            <h1>Login</h1>
            <div>
                <div>
                    <p>Login to your account</p>
                </div>
                <form>
                    <input type="email" placeholder="Email" />
                    <input type="password" placeholder="Password" />
                    <button type="submit">Login</button>
                </form>
            </div>
        </div>
    );
};

export default LoginPage;
import { useContext, useEffect, useMemo, useState } from "react";
import { Input } from "@headlessui/react";
import { useNavigate } from "react-router";
import { AuthContext } from "../../components/context/AuthContext";
import CoreBase from "../core/base";
import { authClient } from "../../lib/auth";
import { Passkey } from "better-auth/plugins/passkey";

const LoginPage = () => {
  const { login } = useContext(AuthContext);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [passkeys, setPasskeys] = useState<Passkey[]>([]);

  useEffect(() => {
    if (passkeys.length > 0) {
      document.cookie = "hasPasskey=true";
    }
  }, [passkeys]);
  const navigate = useNavigate();

  const handleLogin = async (email: string, password: string) => {
    if (email === "" && password === "") {
      // passkey test
      const data = await authClient.signIn.passkey();

      if (data?.error) {
        console.warn("passkey error", data?.error);
      } else {
        console.info("passkey signin success!");
      }

      authClient.passkey.listUserPasskeys().then((data) => {
        if (data.data) setPasskeys(data.data);
      });
    } else {
      try {
        await login(email, password);
        navigate("/dashboard");
      } catch (error: any) {
        if (error.status == 401) {
          setError("Invalid email or password.");
        } else {
          setError("An error occurred. Please try again.");
        }
      }
    }
  };

  const handlePasskeyCreation = async () => {
    // create an authed session if the user did not have one
    const user = await authClient.signIn.anonymous();

    console.log(user);

    const passkeyData = await authClient.passkey.addPasskey({
      name: "Convergemt",
      useAutoRegister: true,
    });

    console.log(passkeyData?.data);
    console.log(passkeyData?.error);
    authClient.passkey.listUserPasskeys().then((data) => {
      if (data.data) setPasskeys(data.data);
    });
  };

  useEffect(() => {
    if (document.cookie.includes("hasPasskey=true")) {
      setPasskeys([{ aaguid: "stored" }]);
    }

    authClient.passkey.listUserPasskeys().then((data) => {
      if (data.data) setPasskeys(data.data);
    });
    if (
      !PublicKeyCredential.isConditionalMediationAvailable ||
      !PublicKeyCredential.isConditionalMediationAvailable()
    ) {
      return;
    }

    void authClient.signIn.passkey({ autoFill: true });
  }, []);

  const noInput = useMemo(() => {
    return email === "" && password === "";
  }, [email, password]);

  return (
    <CoreBase>
      <div
        id="sign-in-container"
        className="flex-2 w-full h-full flex justify-center p-8 md:p-0"
      >
        <form
          className="flex flex-col justify-center"
          onSubmit={(e) => {
            e.preventDefault();
            handleLogin(email, password);
          }}
        >
          {error && (
            <div className="bg-red-500 text-white p-2 rounded-md mb-4 absolute top-16 self-center">
              {error}
            </div>
          )}
          <h2 className="text-5xl font-bold mb-8">Sign In</h2>
          {passkeys.map((data) => (
            <button
              type="button"
              className="border-2 border-gray-500 p-2 rounded-xl"
            >
              <h2>Passkey found! Click to continue</h2>
              {`${data.aaguid}`}
            </button>
          ))}
          {passkeys.length > 0 && (
            <button
              type="button"
              className="border-2 border-gray-500 p-2 rounded-xl"
              onClick={() => authClient.signOut()}
            >
              Log out
            </button>
          )}
          {passkeys.length === 0 && (
            <>
              <input
                className="mb-4 bg-gray-100 rounded-md p-2"
                placeholder="Email"
                value={email}
                autoComplete="username webauthn"
                onChange={(e) => setEmail(e.target.value)}
              />
              <Input
                className="mb-4 bg-gray-100 rounded-md p-2"
                placeholder="Password"
                type="password"
                autoComplete="current-password webauthn"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                className="mb-8 p-2 bg-gray-500 hover:bg-secondary text-white rounded-md"
                onClick={() => handleLogin(email, password)}
              >
                Sign in{noInput ? " with passkey" : ""}
              </button>
              <button
                type="button"
                className="mb-8 p-2 bg-gray-500 hover:bg-secondary text-white rounded-md"
                onClick={handlePasskeyCreation}
              >
                Create a passkey
              </button>
            </>
          )}

          <p>
            Don't have an account?{" "}
            <a href="/register" className="text-text-secondary">
              Register here.
            </a>
          </p>
        </form>
      </div>
    </CoreBase>
  );
};

export default LoginPage;

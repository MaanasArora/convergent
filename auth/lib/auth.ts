import { betterAuth } from "better-auth";
import { Pool } from "pg";
import { passkey } from "better-auth/plugins/passkey";
export const auth = betterAuth({
  database: new Pool({
    user: "user",
    password: "password",
    host: "localhost",
    port: 5432,
    database: "convergent",
  }),
  emailAndPassword: {
    enabled: true,
  },
  plugins: [passkey()],
});

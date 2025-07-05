import type { Preview } from "@storybook/react-vite";

import { initialize, mswLoader } from "msw-storybook-addon";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import "../src/index.css"; // tailwind CSS etc

let options = {};
if (location.hostname.includes("github.io")) {
  options = {
    serviceWorker: {
      url: "/convergent/mockServiceWorker.js", // manually pointing msw config file
    },
  };
}

initialize(options);

const preview: Preview = {
  decorators: [
    (Story) => {
      const queryClient = new QueryClient();

      return (
        <QueryClientProvider client={queryClient}>
          <Story />
        </QueryClientProvider>
      );
    },
  ],
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: "todo",
    },
  },
  loaders: [mswLoader],
};

export default preview;

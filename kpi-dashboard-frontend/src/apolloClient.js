import { ApolloClient, InMemoryCache, HttpLink } from "@apollo/client";

export const client = new ApolloClient({
  link: new HttpLink({ uri: "http://localhost:8023/graphql" }),
  cache: new InMemoryCache(),
});

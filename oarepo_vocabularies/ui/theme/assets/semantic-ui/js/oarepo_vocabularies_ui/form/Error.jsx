import React from "react";
import { Message, Icon } from "semantic-ui-react";

export const ErrorComponent = ({ message }) => {
  console.log(message);
  return (
    <Message negative>
      <Icon name="warning" size="large" />
      {message}
    </Message>
  );
};

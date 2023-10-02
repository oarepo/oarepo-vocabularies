import React from "react";
import { Container } from "semantic-ui-react";
import { NewItemButton } from "../NewItemButton";
import { ClearFiltersButton } from "../ClearFiltersButton";

export const VocabularyButtonSidebar = () => {
  return (
    <Container>
      <NewItemButton />
      <ClearFiltersButton />
    </Container>
  );
};

import React from "react";
import { Card, Grid } from "semantic-ui-react";
import { PublishButton, ResetButton, FeaturedButton } from "../../components";
import { useLocation } from "react-router-dom";

export const VocabularyFormControlPanel = () => {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");
  return (
    <Card fluid>
      <Card.Content>
        <Grid>
          <Grid.Column width={16}>
            <PublishButton newChildItemParentId={newChildItemParentId} />
          </Grid.Column>
          <Grid.Column width={16}>
            <FeaturedButton
              fluid
              color="green"
              icon="upload"
              labelPosition="left"
              type="button"
            />
          </Grid.Column>
          <Grid.Column width={16}>
            <ResetButton />
          </Grid.Column>
        </Grid>
      </Card.Content>
    </Card>
  );
};

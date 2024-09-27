import * as React from "react";
import PropTypes from "prop-types";
import { Grid, Breadcrumb, Button, Label, Icon } from "semantic-ui-react";

export const TreeSelectValues = ({ selected, onRemove }) => (
  <Grid.Row className="gapped">
    {selected.map((value) => (
      <Label key={value.hierarchy.title}>
        {" "}
        <Breadcrumb icon="left angle" sections={value.hierarchy.title} />
        <Button
          className="small transparent"
          onClick={(e) => {
            onRemove(value, e);
          }}
        >
          <Icon name="delete" />
        </Button>
      </Label>
    ))}
  </Grid.Row>
);

TreeSelectValues.propTypes = {
  onRemove: PropTypes.func,
  selectedState: PropTypes.array,
};

export default TreeSelectValues;

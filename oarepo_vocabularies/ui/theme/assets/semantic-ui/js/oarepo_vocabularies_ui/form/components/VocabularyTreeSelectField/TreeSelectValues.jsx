import * as React from "react";
import PropTypes from "prop-types";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui/util";
import { Grid, Breadcrumb, Button, Label, Icon } from "semantic-ui-react";

export const TreeSelectValues = ({ selected = [], onRemove }) => {
  return (
    <Grid.Row className="gapped">
      {selected.map((item) => (
        <Label key={item.value}>
          <Breadcrumb
            icon="left angle"
            sections={item.hierarchy.title.map((t, level) => ({
              key: `${t}-${level}`,
              children: getTitleFromMultilingualObject(t),
            }))}
          />
          <Button
            className="small transparent"
            onClick={(e) => {
              onRemove(item, e);
            }}
          >
            <Icon name="delete" />
          </Button>
        </Label>
      ))}
    </Grid.Row>
  );
};
/* eslint-disable react/require-default-props */
TreeSelectValues.propTypes = {
  onRemove: PropTypes.func.isRequired,
  selected: PropTypes.array,
};
/* eslint-enable react/require-default-props */

export default TreeSelectValues;

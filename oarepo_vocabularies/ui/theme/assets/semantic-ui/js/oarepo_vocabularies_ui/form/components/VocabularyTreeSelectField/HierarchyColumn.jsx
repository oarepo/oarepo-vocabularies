import * as React from "react";
import { List, Checkbox, Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { isSelectable } from "./util";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui/util";

export const HierarchyColumn = ({
  items = [],
  level,
  onSelect,
  onExpand,
  onKeyDown,
  currentAncestors,
  multiple,
  selected,
  value,
  isLast,
}) => {
  return (
    <List className="tree-column">
      {items.map((item) => {
        if (
          level === 0 ||
          item.hierarchy.ancestors[0] === currentAncestors[level - 1]
        ) {
          return (
            <List.Item
              key={item.value}
              className={
                item.value === currentAncestors[level] ||
                item.value === value.id
                  ? "open spaced"
                  : "spaced"
              }
            >
              <List.Content
                onClick={(e) =>
                  multiple || !isSelectable(item)
                    ? onExpand(item.value, level)()
                    : onSelect(item, e)
                }
                onDoubleClick={(e) => {
                  onSelect(item, e);
                }}
                onKeyDown={(e) => {
                  onKeyDown(e, level);
                }}
                tabIndex={0}
              >
                {multiple && (
                  <Checkbox
                    checked={
                      selected.findIndex((opt) => opt.value === item.value) !==
                      -1
                    }
                    disabled={!isSelectable(item)}
                    indeterminate={selected.some((opt) =>
                      opt.hierarchy.ancestors.includes(item.value)
                    )}
                    onChange={(e) => {
                      onSelect(item, e);
                    }}
                  />
                )}
                {getTitleFromMultilingualObject(item.hierarchy.title[0])}
              </List.Content>

              {!item.hierarchy.leaf && (
                <Button
                  className="transparent"
                  onClick={onExpand(item.value, level)}
                >
                  {isLast && <Icon name="angle right" color="black" />}
                </Button>
              )}
            </List.Item>
          );
        }
        return null;
      })}
    </List>
  );
};

/* eslint-disable react/require-default-props */
HierarchyColumn.propTypes = {
  level: PropTypes.number.isRequired,
  items: PropTypes.array,
  onSelect: PropTypes.func.isRequired,
  onExpand: PropTypes.func.isRequired,
  onKeyDown: PropTypes.func.isRequired,
  selected: PropTypes.array.isRequired,
  currentAncestors: PropTypes.array.isRequired,
  value: PropTypes.oneOfType([PropTypes.object, PropTypes.array]).isRequired,
  multiple: PropTypes.bool,
  isLast: PropTypes.bool,
};
/* eslint-enable react/require-default-props */

export default HierarchyColumn;

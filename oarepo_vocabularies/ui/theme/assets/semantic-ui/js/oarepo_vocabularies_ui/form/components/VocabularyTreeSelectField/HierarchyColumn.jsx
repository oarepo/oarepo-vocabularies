import * as React from "react";
import { List, Checkbox, Button, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { isSelectable } from "./util";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui";

export const HierarchyColumn = ({
  items,
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

              {item.element_type === "parent" && (
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
      })}
    </List>
  );
};

HierarchyColumn.propTypes = {
  level: PropTypes.number,
  items: PropTypes.array,
  onSelect: PropTypes.func,
  onExpand: PropTypes.func,
  onKeyDown: PropTypes.func,
  selected: PropTypes.oneOfType([PropTypes.array, PropTypes.object]).isRequired,
  currentAncestors: PropTypes.array,
  value: PropTypes.oneOfType([PropTypes.array, PropTypes.object]).isRequired,
  multiple: PropTypes.bool,
  isLast: PropTypes.bool,
};

HierarchyColumn.defaultProps = {
  items: [],
};

export default HierarchyColumn;

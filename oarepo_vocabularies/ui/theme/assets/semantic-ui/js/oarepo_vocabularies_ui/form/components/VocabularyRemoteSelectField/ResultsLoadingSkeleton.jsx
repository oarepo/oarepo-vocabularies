import * as React from "react";
import { OptionsLoadingSkeleton } from "../OptionsLoadingSkeleton";
import { withState } from "react-searchkit";

export const ResultsLoadingSkeleton = withState(
  ({ currentResultsState: results, loadingMessage }) => (
    <OptionsLoadingSkeleton
      loading={results.loading}
      loadingMessage={loadingMessage}
    />
  )
);

export default ResultsLoadingSkeleton;

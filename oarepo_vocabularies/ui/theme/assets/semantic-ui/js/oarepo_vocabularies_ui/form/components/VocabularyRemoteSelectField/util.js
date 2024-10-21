
export const featuredFilterActive = (currentQueryState) => {
    const { filters } = currentQueryState;
    return filters.some(
        (f) => f[0] === "tags" && f[1] === "featured"
    );
}

export function inSuggestMode (currentQueryState) {
    return currentQueryState.suggestions?.length > 0 &&
        currentQueryState.queryString === "" &&
        currentQueryState.suggestionString !== ""
}
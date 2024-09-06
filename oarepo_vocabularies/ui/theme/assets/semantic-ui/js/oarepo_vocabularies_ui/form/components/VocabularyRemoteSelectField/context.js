import * as React from 'react'
import PropTypes from 'prop-types'

export const FieldValueContext = React.createContext();

export const FieldValueProvider = ({ children, value, multiple }) => {
    return (
        <FieldValueContext.Provider value={{ value, multiple }}>
            {children}
        </FieldValueContext.Provider>
    );
};

FieldValueProvider.propTypes = {
    value: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
    multiple: PropTypes.bool,
    children: PropTypes.node
}


export const useFieldValue = () => {
    const context = React.useContext(FieldValueContext);
    if (!context) {
        throw new Error(
            "useFieldValue must be used inside FieldValueProvider"
        );
    }
    return context.value;
}
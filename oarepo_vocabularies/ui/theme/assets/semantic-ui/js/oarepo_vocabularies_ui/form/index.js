
import React from "react";
import ReactDOM from "react-dom";
import { getInputFromDOM } from '../util';
import { OverridableContext, overrideStore } from "react-overridable";

const vocabularyRecord = getInputFromDOM('vocabulary-record')
const formConfig = getInputFromDOM('form-config')
const appRoot = document.getElementById('vocabulary-form')

export const overriddenComponents = {}

// TODO: remove when not needed for development
console.debug('[vocabularyRecord]:', vocabularyRecord, '\n[formConfig]', formConfig)

ReactDOM.render(
    <OverridableContext.Provider value={overriddenComponents}>
        // TODO: (ducica) here we should initialize and render vocabulary form
        {/* <VocabularyForm vocabularyRecord={vocabularyRecord} config={formConfig} /> */}
    </OverridableContext.Provider>,
    appRoot
)

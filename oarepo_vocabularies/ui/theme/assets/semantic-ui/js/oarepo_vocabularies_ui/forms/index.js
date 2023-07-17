import React from 'react'
import { createFormAppInit, useFormConfig } from '@js/oarepo_ui/forms'

// TODO(ducica): Provide your form layout here
// To access the form config values, use the following hook in your components:
// 
// import {useFormConfig} from '@js/oarepo_ui/forms'
// const {record, formConfig, recordPermissions} = useFormConfig()

const ExampleVocabularyFormLayout = () => {
    const { record, formConfig, recordPermissions } = useFormConfig()
    return (
      <div>
        <div>
          <p>Your example vocabulary form here</p>
        </div>
        <div>
          <h2>Record data</h2>
          <pre>{JSON.stringify(record, null, 4)}</pre>
          <h2>Form Config</h2>
          <pre>{JSON.stringify(formConfig, null, 4)}</pre>
          <h2>Record permissions</h2>
          <pre>{JSON.stringify(recordPermissions, null, 4)}</pre>
        </div>
      </div>
    );
}

export const overriddenComponents = {
    'FormApp.layout': ExampleVocabularyFormLayout
}

createFormAppInit(overriddenComponents)
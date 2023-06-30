
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
        <p>An example vocabulary form here</p>
        <pre>{JSON.stringify(record)}</pre>
        <pre>{JSON.stringify(formConfig)}</pre>
        <pre>{JSON.stringify(recordPermissions)}</pre>
      </div>
    );
}

export const overriddenComponents = {
    'FormApp.layout': ExampleVocabularyFormLayout
}

createFormAppInit(overriddenComponents)
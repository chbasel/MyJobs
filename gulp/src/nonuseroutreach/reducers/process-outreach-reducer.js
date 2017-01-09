import {handleActions} from 'redux-actions';
import {isEmpty, get, has, includes, forOwn, map} from 'lodash-compat';

const defaultState = {
  record: {
    partner: {},
    contacts: [],
    communication_record: {},
  },
  newTags: {},
};

export function getErrorsForForm(forms, key) {
  return !isEmpty(get(forms, [key, 'errors']));
}

export function getErrorsForForms(forms, key) {
  return map(get(forms, key), f => !isEmpty(get(f, 'errors')));
}


/**
 * Represents the state of processing an NUO outreach record. {
 *
 *  state: string constant, What the user is doing right now.
 *    SELECT_PARTNER: the user is selecting a partner (or contact)
 *    NEW_PARTNER: the user is editing a new partner
 *    SELECT_CONTACT: the user is selecting a contact AFTER selecting a partner
 *    NEW_CONTACT: the user is editng a new contact
 *    CONTACT_APPEND: the user is adding notes to an existing contact
 *    NEW_COMMUNICATIONRECORD: the user is editing the new record
 *    SELECT_WORKFLOW_STATE: the user is picking the new workflow state
 *
 *  outreach: information for the current outreach record
 *  workflowStates: list of known workflow states {value:.., display:..}
 *  contactIndex: if editing a contact, which one is the user concerned with?
 *  blankForms: form data from Django defining available form fields.
 *  forms: form data from Django defining state of entered data, errors, etc.
 *  record: The record which will be submitted {
 *    outreachrecord: the outreach record we are working on
 *    partner: field contents for new partner
 *    contacts: [{ field contents for new contacts}]
 *    communication_record: field contents for record
 *  }
 *  dirty: the user could lose work if they leave
 */
export default handleActions({
  'NUO_RESET_PROCESS': (state, action) => {
    const {
      outreach,
      blankForms,
    } = action.payload;

    return {
      ...defaultState,
      state: 'SELECT_PARTNER',
      blankForms,
      forms: {
        contacts: [],
        outreach_record: blankForms.outreach_record,
      },
      outreach,
    };
  },

  'NUO_DETERMINE_STATE': (state) => {
    let currentState;
    let newForms = state.forms;
    let contactIndex = state.contactIndex;

    // Test if your current form has errors, if so stay there.
    if (state.state === 'NEW_PARTNER' && getErrorsForForm(state.forms, 'partner')) {
      currentState = state.state;
    } else if (['CONTACT_APPEND', 'NEW_CONTACT'].indexOf(state.state) !== -1 &&
               getErrorsForForms(state.forms, 'contacts')[contactIndex]) {
      currentState = state.state;
    } else if (state.state === 'NEW_COMMUNICATIONRECORD' && getErrorsForForm(state.forms, 'communication_record')) {
      currentState = state.state;

    // Traverse through forms looking for the first one that does not have data, or has errors.
    } else if (isEmpty(state.record.partner)) {
      currentState = 'SELECT_PARTNER';
    } else if (getErrorsForForm(state.forms, 'partner')) {
      currentState = 'NEW_PARTNER';
    } else if (isEmpty(state.record.contacts)) {
      currentState = 'SELECT_CONTACT';
    } else if (getErrorsForForms(state.forms, 'contacts').indexOf(true) !== -1) {
      currentState = 'NEW_CONTACT';
      contactIndex = getErrorsForForms(state.forms, 'contacts').indexOf(true);
    } else if (isEmpty(state.record.communication_record) || getErrorsForForm(state.forms, 'communication_record')) {
      currentState = 'NEW_COMMUNICATIONRECORD';
      newForms = {
        ...state.forms,
        communication_record: state.blankForms.communication_record,
      };
    } else {
      currentState = 'SELECT_WORKFLOW_STATE';
    }
    return {
      ...state,
      state: currentState,
      forms: newForms,
      contactIndex: contactIndex,
    };
  },

  'NUO_CHOOSE_PARTNER': (state, action) => {
    const {name, partnerId} = action.payload;

    return {
      ...state,
      dirty: true,
      record: {
        ...state.record,
        partner: {
          pk: partnerId,
          name: name,
        },
      },
    };
  },

  'NUO_CHOOSE_CONTACT': (state, action) => {
    const {name, contactId} = action.payload;

    return {
      ...state,
      dirty: true,
      forms: {
        ...state.forms,
        contacts: [
          ...state.forms.contacts,
          null,
        ],
      },
      record: {
        ...state.record,
        contacts: [
          ...state.record.contacts,
          {
            pk: contactId,
            name: name,
          },
        ],
      },
    };
  },

  'NUO_NEW_PARTNER': (state, action) => {
    const {partnerName} = action.payload;

    const newState = {
      ...state,
      dirty: true,
      state: 'NEW_PARTNER',
      forms: {
        ...state.forms,
        partner: state.blankForms.partner,
      },
      record: {
        ...state.record,
        partner: {
          pk: '',
          name: partnerName,
        },
      },
    };

    delete newState.contactId;
    delete newState.contact;

    return newState;
  },

  'NUO_NEW_CONTACT': (state, action) => {
    const {contactName} = action.payload;
    const {contacts} = state.record;
    const newIndex = contacts.length;

    const newState = {
      ...state,
      dirty: true,
      state: 'NEW_CONTACT',
      contactIndex: newIndex,
      forms: {
        ...state.forms,
        contacts: [
          ...state.forms.contacts,
          state.blankForms.contact,
        ],
      },
      record: {
        ...state.record,
        contacts: [
          ...state.record.contacts,
          {
            pk: '',
            name: contactName,
          },
        ],
      },
    };

    return newState;
  },

  'NUO_EDIT_PARTNER': (state) => {
    return {
      ...state,
      state: 'NEW_PARTNER',
    };
  },

  'NUO_EDIT_CONTACT': (state, action) => {
    const {contactIndex} = action.payload;

    const pk = get(state, ['record', 'contacts', contactIndex, 'pk']);
    const newState = pk ? 'CONTACT_APPEND' : 'NEW_CONTACT';
    return {
      ...state,
      state: newState,
      contactIndex,
    };
  },

  'NUO_EDIT_COMMUNICATIONRECORD': (state) => {
    return {
      ...state,
      state: 'NEW_COMMUNICATIONRECORD',
    };
  },

  'NUO_DELETE_PARTNER': (state) => {
    // filter out contacts with a PK (i.e. existing contacts that would be
    // linked to the soon-to-be-removed parter
    const newContacts = state.record.contacts.filter(contact => !contact.pk);
    return {
      ...state,
      record: {
        ...state.record,
        partner: {},
        contacts: newContacts,
      },
    };
  },

  'NUO_DELETE_CONTACT': (state, action) => {
    const {contactIndex} = action.payload;
    const splicedContacts = state.record.contacts.slice();
    splicedContacts.splice(contactIndex, 1);

    return {
      ...state,
      record: {
        ...state.record,
        contacts: splicedContacts,
      },
    };
  },


  'NUO_DELETE_COMMUNICATIONRECORD': (state) => {
    return {
      ...state,
      record: {
        ...state.record,
        communication_record: {},
      },
    };
  },

  'NUO_RECEIVE_FORM': (state, action) => {
    const {form} = action.payload;

    return {
      ...state,
      form,
    };
  },

  'NUO_EDIT_FORM': (state, action) => {
    const {form: formName, formIndex, field, value} = action.payload;

    if (formIndex || formIndex === 0) {
      const formSet = (state.record || {})[formName] || [];
      const form = formSet[formIndex] || {};

      const newForm = {
        ...form,
        [field]: value,
      };

      const newFormSet = [...formSet];
      newFormSet[formIndex] = newForm;

      return {
        ...state,
        dirty: true,
        record: {
          ...state.record,
          [formName]: newFormSet,
        },
      };
    }

    const form = (state.record || {})[formName] || {};

    return {
      ...state,
      dirty: true,
      record: {
        ...state.record,
        [formName]: {
          ...form,
          [field]: value,
        },
      },
    };
  },

  'NUO_MARK_CLEAN': (state) => {
    return {
      ...state,
      dirty: false,
    };
  },

  'NUO_ADD_NEW_TAG': (state, action) => {
    const {form, tagName} = action.payload;
    const {newTags} = state;
    if (has(newTags, tagName)) {
      if (!includes(newTags[tagName], form)) {
        newTags[tagName].push(form);
      }
    } else {
      newTags[tagName] = [form];
    }
    return {
      ...state,
      newTags: {
        ...newTags,
      },
    };
  },

  'NUO_REMOVE_NEW_TAG': (state, action) => {
    const {form, tagName} = action.payload;
    const {newTags} = state;

    if (has(newTags, tagName)) {
      if (includes(newTags[tagName], form)) {
        newTags[tagName].splice(newTags[tagName].indexOf(form), 1);
      }
    }
    return {
      ...state,
      newTags: {
        ...newTags,
      },
    };
  },

  'NUO_REMOVE_NEW_TAGS_FROM_FORM': (state, action) => {
    const form = action.payload;
    const {newTags} = state;
    const returnTags = {};
    forOwn(newTags, (value, key) => {
      if (includes(value, form)) {
        value.splice(value.indexOf(form), 1);
      }
      returnTags[key] = value;
    });
    return {
      ...state,
      newTags: {
        ...returnTags,
      },
    };
  },

  'NUO_CLEANUP_ORPHAN_TAGS': (state) => {
    const {newTags} = state;
    const remainingTags = {};
    forOwn(newTags, (value, key) => {
      if (!isEmpty(value)) remainingTags[key] = value;
    });
    return {
      ...state,
      newTags: {
        ...remainingTags,
      },
    };
  },

  'NUO_NOTE_FORMS': (state, action) => {
    const {record, forms} = action.payload;

    return {
      ...state,
      forms,
      record,
    };
  },
}, defaultState);

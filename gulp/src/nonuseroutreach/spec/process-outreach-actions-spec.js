import processEmailReducer from '../reducers/process-outreach-reducer';
import errorReducer from '../../common/reducers/error-reducer';
import {keys, mapValues} from 'lodash-compat';

import {
  doLoadEmail,
  resetProcessAction,
  convertOutreach,
  extractErrorObject,
  formatContact,
  flattenContact,
  formsFromApi,
  formsToApi,
} from '../actions/process-outreach-actions';

import {promiseTest} from '../../common/spec';

import createReduxStore from '../../common/create-redux-store';
import {combineReducers} from 'redux';

class FakeApi {
  getOutreach() {}
  getForms() {}
}

describe('convertOutreach', () => {
  const record = {
    date_added: "06-17-2016",
    from_email: "bob@example.com",
    email_body: "some text",
    outreach_email: "testemail@my.jobs",
    current_workflow_state: "Reviewed",
    subject: "Subject",
    cc_emails: "cc@example.com",
    to_emails: "to@example.com"
  };
  const result = convertOutreach(record);

  it('should change the keys of fields', () => {
    expect(result).toDiffEqual({
      dateAdded: "06-17-2016",
      outreachFrom: "bob@example.com",
      outreachBody: "some text",
      outreachInbox: "testemail@my.jobs",
      workflowState: "Reviewed",
      outreachSubject: "Subject",
      outreachCC: "cc@example.com",
      outreachTo: "to@example.com",
    });
  });
});

describe('initial load', () => {
  let store;
  let api;

  beforeEach(() => {
    api = new FakeApi();
    store = createReduxStore(
      combineReducers({process: processEmailReducer, error: errorReducer}),
      {}, {api});
  });

  describe('after load', () => {
    const outreach = {
      from_email: "bob@example.com",
      email_body: "some text",
    };
    const blankForms = {
      6: {fields: {widget: { }}},
    };

    beforeEach(promiseTest(async () => {
      spyOn(api, 'getOutreach').and.returnValue(Promise.resolve(outreach));
      spyOn(api, 'getForms').and.returnValue(Promise.resolve({6: 7}));
      await store.dispatch(doLoadEmail(2));
    }));

    it('should have the outreach', () => {
      expect(store.getState().process.outreach).toDiffEqual(
        convertOutreach(outreach));
    });

    it('should have the outreachId', () => {
      expect(store.getState().process.record.outreach_record.pk).toEqual(2);
    });

    it('should have the blank forms', () => {
      expect(store.getState().process.blankForms).toEqual({6: {fields: {}}});
    });

    it('should be in the right state', () => {
      expect(store.getState().process.state).toEqual('SELECT_PARTNER');
    });
  });

  describe('after an error', () => {
    beforeEach(promiseTest(async () => {
      spyOn(api, 'getOutreach').and.throwError('some error');
      await store.dispatch(doLoadEmail(2));
    }));

    it('should remember the error', () => {
      expect(store.getState().error.lastMessage).toEqual('some error');
    });
  });

  describe('colorizeTagsInForms: ', () => {
    const communicationRecord = {
      fields: {
        tags: {
          widget: {
            attrs: {
              tag_colors: {
                930: {hex_color: "5EB94E"},
              },
              choices: [{display: "Veteran", value: 930},]
            },
            input_type: "selectmultiple",
          },
        },
      },
    };

    function colorizeTagsInForms(forms) {
      const responseWithColoredTags = mapValues(forms, form => ({
        ...form,
        fields: mapValues(form.fields, field => {
          if (field.widget.input_type === 'selectmultiple') {
            const newField = {
              ...field,
              choices: map(field.choices, c => ({
                ...c,
                hexColor:
                  field.widget.attrs.tag_colors[c.value].hex_color,
              })),
            };
            return newField;
          }
          return field;
        }),
      }));
      return responseWithColoredTags;
    }

    function expectKeys(forms) {
      return expect(colorizeTagsInForms(forms));
    }

    it('should match api response with "tag_color" object', () => {
      const expected = {
          fields: {
            tags: {
              widget: {
                attrs: {
                  tag_colors: {
                    930: {hex_color: "5EB94E"},
                  },
                  choices: [{display: "Veteran", value: 930},]
                },
                input_type: "selectmultiple",
              },
            },
          fields: {},
          },
        };
      expectKeys(communicationRecord).toEqual(expected);
    });
  });
});



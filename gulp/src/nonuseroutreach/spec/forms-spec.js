import {map} from 'lodash-compat';
import {pruneCommunicationRecordForm} from '../forms.js';

describe('pruneCommunicationRecordForm', () => {
  const fullForm = {
    data: {},
    errors: {},
    fields: {
      contact_type: {
        choices: [
          {"display": "---------", "value": ""},
          {"display": "Email", "value": "email"},
          {"display": "Phone", "value": "phone"},
          {"display": "Meeting or Event", "value": "meetingorevent"},
          {"display": "Job Followup", "value": "job"},
          {"display": "Partner Saved Search Email", "value": "pssemail"},
        ],
      },
    },
    ordered_fields: [
      "contact_type",
      "contact_email",
      "contact_phone",
      "location",
      "length",
      "subject",
      "date_time",
      "job_id",
      "job_applications",
      "job_interviews",
      "job_hires",
      "tags",
      "notes"
    ],
  };

  function expectKeys(form, formContents) {
    return expect(pruneCommunicationRecordForm(form, formContents)
      .ordered_fields);
  }

  it('handles untyped', () => {
    const expected = [
      'contact_type',
      'subject',
      'date_time',
      'tags',
      'notes',
    ];
    expectKeys(fullForm).toDiffEqual(expected);
    expectKeys(fullForm, {}).toDiffEqual(expected);
    expectKeys(fullForm, {contact_type: undefined}).toDiffEqual(expected);
    expectKeys(fullForm, {contact_type: ''}).toDiffEqual(expected);
    expectKeys(fullForm, {contact_type: 'ZZZZ'}).toDiffEqual(expected);
  });

  it('handles email', () => {
    expectKeys(fullForm, {contact_type: 'email'}).toDiffEqual([
      'contact_type',
      'contact_email',
      'subject',
      'date_time',
      'tags',
      'notes',
    ]);
  });

  it('preserves other fields', () => {
    const result = pruneCommunicationRecordForm(fullForm);
    expect(result.data).toBe(fullForm.data);
    expect(result.errors).toBe(fullForm.errors);
  });

  it('prunes the contact_type choice list', () => {
    const result = pruneCommunicationRecordForm(fullForm);
    expect(map(result.fields.contact_type.choices, t => t.value))
      .toDiffEqual(['', 'email', 'phone', 'meetingorevent']);
  });
});

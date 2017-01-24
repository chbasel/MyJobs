import React, {PropTypes, Component} from 'react';
import {connect} from 'react-redux';
import FieldWrapper from 'common/ui/FieldWrapper';
import Card from './Card';
import Form from './Form';
import SearchDrop from './SearchDrop';
import {
  get,
  forEach,
  includes,
  sortBy,
  map,
  keys,
  pick,
  without,
  indexBy,
} from 'lodash-compat';


import {
  contactNotesOnlyForm,
  pruneCommunicationRecordForm,
  replaceStateWithChoices,
} from 'nonuseroutreach/forms';

import {
  resetSearchOrAddAction,
} from '../actions/search-or-add-actions';

import {
  determineProcessStateAction,
  choosePartnerAction,
  chooseContactAction,
  newPartnerAction,
  newContactAction,
  editFormAction,
  removeNewTagAction,
  addNewTagAction,
  doSubmit,
  cleanUpOrphanTags,
} from '../actions/process-outreach-actions';

class ProcessRecordPage extends Component {

  getAvailableTags(form) {
    const {newTags} = this.props;
    const existingTags = form.fields.tags.choices;

    return sortBy([
      ...existingTags,
      ...map(keys(newTags), tagName => ({value: tagName, display: tagName})),
    ], 'display');
  }

  getSelectedTagsForForm(formName, form, formContents) {
    const {newTags} = this.props;
    const existingTags = indexBy(form.fields.tags.choices, 'value');

    return sortBy([
      ...map(formContents.tags || [], v => existingTags[v]),
      ...map(keys(pick(newTags, assoc => includes(assoc, formName))), v =>
        ({value: v, display: v})),
    ], 'display');
  }

  handleNewTag(form, tagName) {
    const {dispatch} = this.props;
    dispatch(addNewTagAction(form, tagName));
  }

  handleRemoveTag(formName, formKey, formIndex, formContents, tags) {
    const {dispatch} = this.props;
    forEach(tags, (tag) => {
      if (tag.value === tag.display) {
        dispatch(removeNewTagAction(formName, tag.display));
      } else {
        const value = without(formContents.tags, ...map(tags, t => t.value));
        dispatch(editFormAction(formKey, 'tags', value, formIndex));
      }
    });
  }

  handleSelectTag(formName, formKey, formIndex, formContents, tags) {
    const {dispatch} = this.props;
    forEach(tags, (tag) => {
      if (tag.value === tag.display) {
        dispatch(addNewTagAction(formName, tag.display));
      } else {
        const value = [...formContents.tags || [], tag.value];
        dispatch(editFormAction(formKey, 'tags', value, formIndex));
      }
    });
  }

  /**
   * router for tag related action. reduces number of prop types provided to
   * form, remoteformfield
   *
   * @param action - what action is taking place, added via curried function
   * @param form - the name of the form being accessed
   * @param tagNameOrObject - either a tag name or tag object
   */

  tagActionRouter(action, formName, formKey, formIndex, formContents, tagNameOrObjects) {
    switch (action) {
    case 'remove':
      this.handleRemoveTag(formName, formKey, formIndex, formContents, tagNameOrObjects);
      break;
    case 'select':
      this.handleSelectTag(formName, formKey, formIndex, formContents, tagNameOrObjects);
      break;
    case 'new':
      this.handleNewTag(formName, tagNameOrObjects);
      break;
    default:
      break;
    }
  }

  resetSearches() {
    const {dispatch} = this.props;

    dispatch(resetSearchOrAddAction('PARTNER'));
    dispatch(resetSearchOrAddAction('CONTACT'));
  }

  async handleChoosePartner(obj) {
    const {dispatch} = this.props;

    dispatch(choosePartnerAction(obj.value, obj.display));
    this.resetSearches();
    await(dispatch(doSubmit(true)));
    dispatch(determineProcessStateAction());
  }

  async handleChooseContact(obj, addPartner) {
    const {dispatch} = this.props;

    if (addPartner) {
      dispatch(choosePartnerAction(obj.partner.pk, obj.partner.name));
    }
    dispatch(chooseContactAction(obj.value, obj.display));
    this.resetSearches();
    await(dispatch(doSubmit(true)));
    dispatch(determineProcessStateAction());
  }

  async handleNewPartner(obj) {
    const {dispatch} = this.props;
    dispatch(newPartnerAction(obj.display));
  }

  async handleNewContact(obj) {
    const {dispatch} = this.props;
    dispatch(newContactAction(obj.display));
  }

  async handleSavePartner() {
    const {dispatch} = this.props;
    await dispatch(doSubmit(true, () => this.scrollToTop()));
    this.resetSearches();
    dispatch(determineProcessStateAction());
  }

  async handleSaveContact() {
    const {dispatch} = this.props;
    await dispatch(doSubmit(true, () => this.scrollToTop()));
    this.resetSearches();
    dispatch(determineProcessStateAction());
  }

  async handleSaveCommunicationRecord() {
    const {dispatch} = this.props;
    await dispatch(doSubmit(true, () => this.scrollToTop()));
    this.resetSearches();
    dispatch(determineProcessStateAction());
  }

  async handleSubmit() {
    const {dispatch, history} = this.props;
    dispatch(cleanUpOrphanTags());
    await dispatch(doSubmit(false, () => this.scrollToTop(), () => history.pushState(null, '/records')));
    this.resetSearches();
  }

  scrollToTop() {
    document.body.scrollTop = document.documentElement.scrollTop = 0;
  }

  renderCard(title, children) {
    return (
      <Card title={title}>
        {children}
      </Card>
    );
  }

  renderInitialSearch() {
    return this.renderCard('Partner Data', ([
      <div key="partner" className="product-card no-highlight clearfix">
        <FieldWrapper label="Partner Organization">
          <SearchDrop
            instance="PARTNER"
            onAdd={obj => this.handleNewPartner(obj)}
            onSelect={obj => this.handleChoosePartner(obj)}/>
        </FieldWrapper>
      </div>,
      <div key="contact" className="product-card no-highlight clearfix">
        <FieldWrapper label="Contact Search">
          <SearchDrop
            instance="CONTACT"
            onSelect={obj => this.handleChooseContact(obj, true)}/>
        </FieldWrapper>
      </div>,
    ]));
  }

  renderSelectContact() {
    const {partnerId} = this.props;
    return this.renderCard('Add Contact', ([
      <div key="contact" className="product-card no-highlight clearfix">
        <FieldWrapper label="Contact Search">
          <SearchDrop
            instance="CONTACT"
            extraParams={{partner_id: partnerId}}
            onSelect={obj => this.handleChooseContact(obj, false)}
            onAdd={obj => this.handleNewContact(obj)}
            />
        </FieldWrapper>
      </div>,
    ]));
  }

  renderNewCommunicationRecord() {
    const {
      dispatch,
      communicationRecordForm,
      communicationRecordFormContents,
    } = this.props;

    const prunedForm = pruneCommunicationRecordForm(
      communicationRecordForm, communicationRecordFormContents);

    return (
      <Form
        form={prunedForm}
        title="Communication Record"
        submitTitle="Add Record"
        formContents={communicationRecordFormContents}
        onEdit={(n, v) =>
          dispatch(editFormAction('communication_record', n, v))}
        onSubmit={() => this.handleSaveCommunicationRecord()}
        tagActions={(action, tag) => {
          this.tagActionRouter(
            action,
            'communicationrecord',
            'communication_record',
            undefined,
            communicationRecordFormContents,
            tag);
        }}
        availableTags={this.getAvailableTags(communicationRecordForm)}
        selectedTags={
          this.getSelectedTagsForForm(
            'communicationrecord',
            communicationRecordForm,
            communicationRecordFormContents)}
        />
    );
  }

  renderNewPartner() {
    const {dispatch, partnerForm, partnerFormContents} = this.props;

    return (
      <Form
        form={partnerForm}
        title="Partner Data"
        submitTitle="Add Partner"
        formContents={partnerFormContents}
        onEdit={(n, v) => dispatch(editFormAction('partner', n, v))}
        onSubmit={() => this.handleSavePartner()}
        tagActions={(action, tag) =>
          this.tagActionRouter(
            action,
            'partner',
            'partner',
            undefined,
            partnerFormContents,
            tag)}
        availableTags={this.getAvailableTags(partnerForm)}
        selectedTags={
          this.getSelectedTagsForForm(
            'partner', partnerForm, partnerFormContents)}
        />
    );
  }

  renderNewContact() {
    const {
      dispatch,
      contactIndex,
      contactForms,
      contactFormsContents,
    } = this.props;

    const contactForm = contactForms[contactIndex];
    const contactFormContents = contactFormsContents[contactIndex] || {};

    const modifiedContactForm = replaceStateWithChoices(contactForm, contactFormContents);

    return (
      <Form
        form={modifiedContactForm}
        title="Contact Details"
        submitTitle="Add Contact"
        formContents={contactFormContents}
        onEdit={(n, v) =>
          dispatch(editFormAction('contacts', n, v, contactIndex))}
        onSubmit={() => this.handleSaveContact()}
        tagActions={(action, tag) => {
          this.tagActionRouter(
            action,
            'contact' + contactIndex,
            'contacts',
            contactIndex,
            contactFormContents,
            tag);
        }}
        availableTags={this.getAvailableTags(contactForm)}
        selectedTags={
          this.getSelectedTagsForForm(
            'contact' + contactIndex, contactForm, contactFormContents)}
        />
    );
  }

  renderAppendContactNotes() {
    const {dispatch, contactIndex, contactFormsContents} = this.props;
    const contactFormContents = contactFormsContents[contactIndex] || {};

    return (
      <Form
        form={contactNotesOnlyForm}
        title="Contact Details"
        submitTitle="Add Contact"
        formContents={contactFormContents}
        onEdit={(n, v) =>
          dispatch(editFormAction('contacts', n, v, contactIndex))}
        onSubmit={() => this.handleSaveContact()}
        />
    );
  }

  renderSelectWorkflow() {
    const {
      dispatch,
      outreachRecordForm,
      outreachRecordFormContents,
    } = this.props;

    return (
      <Form
        form={outreachRecordForm}
        title="Form Ready for Submission"
        submitTitle="Submit"
        formContents={outreachRecordFormContents}
        onEdit={(n, v) =>
          dispatch(editFormAction('outreach_record', n, v, null))}
        onSubmit={() => this.handleSubmit()}
        />
    );
  }

  render() {
    const {processState} = this.props;

    let contents = '';
    let extraAddContact = '';

    if (processState === 'SELECT_PARTNER') {
      contents = this.renderInitialSearch();
    } else if (processState === 'SELECT_CONTACT') {
      contents = this.renderSelectContact();
    } else if (processState === 'NEW_COMMUNICATIONRECORD') {
      extraAddContact = this.renderSelectContact();
      contents = this.renderNewCommunicationRecord();
    } else if (processState === 'NEW_PARTNER') {
      contents = this.renderNewPartner();
    } else if (processState === 'NEW_CONTACT') {
      contents = this.renderNewContact();
    } else if (processState === 'CONTACT_APPEND') {
      contents = this.renderAppendContactNotes();
    } else if (processState === 'SELECT_WORKFLOW_STATE') {
      extraAddContact = this.renderSelectContact();
      contents = this.renderSelectWorkflow();
    }

    return (
      <div>
        <button className="nuo-button">
          <a href="/prm/view/nonuseroutreach/#/records">Back to record list</a>
        </button>
        {extraAddContact}
        {contents}
      </div>
    );
  }
}

ProcessRecordPage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  processState: PropTypes.string.isRequired,
  partnerId: PropTypes.any,
  partnerFormContents: PropTypes.object.isRequired,
  contactFormsContents: PropTypes.arrayOf(
    PropTypes.object.isRequired).isRequired,
  outreachRecordFormContents: PropTypes.object,
  contactIndex: PropTypes.number,
  communicationRecordFormContents: PropTypes.object.isRequired,
  newTags: PropTypes.object,
  partnerForm: PropTypes.object,
  contactForms: PropTypes.arrayOf(PropTypes.object),
  communicationRecordForm: PropTypes.object,
  outreachRecordForm: PropTypes.object,
};

export default connect(state => ({
  processState: state.process.state,
  partnerId: get(state.process, 'record.partner.pk'),
  contactIndex: state.process.contactIndex,
  partnerFormContents: state.process.record.partner,
  contactFormsContents: state.process.record.contacts,
  communicationRecordFormContents:
    state.process.record.communication_record,
  newTags: state.process.newTags,
  outreachRecordFormContents: state.process.record.outreach_record,
  partnerForm: state.process.forms.partner,
  contactForms: state.process.forms.contacts,
  communicationRecordForm: state.process.forms.communication_record,
  outreachRecordForm: state.process.forms.outreach_record,
}))(ProcessRecordPage);

/* global $ */
/* global id */
/* global module */

import React from 'react';
import {getCsrf} from 'common/cookie';

import {render} from 'react-dom';
import {Router, Route, IndexRoute} from 'react-router';

import {find} from 'lodash-compat/collection';

import TextField from '../common/ui/TextField';
import CheckBox from '../common/ui/CheckBox';
import Textarea from '../common/ui/Textarea';
import Datetime from '../common/ui/Datetime';
import Select from '../common/ui/Select';
import FieldWrapper from '../common/ui/FieldWrapper';

class Module extends React.Component {
  constructor(props) {
    super(props);

    const {location, params} = this.props;

    const formContents = {};
    formContents.csrfmiddlewaretoken = getCsrf();
    formContents.module = location.query.module;

    // Editing existing module
    if (params.moduleId) {
      formContents.id = params.moduleId;
    } else {
      // Creating new module
      formContents.id = 'new';
    }

    this.state = {
      apiResponse: '',
      formContents: formContents,
    };
    this.callAPI = this.callAPI.bind(this);
  }
  componentDidMount() {
    this.callAPI();
  }
  onChange(event) {
    const fieldID = event.target.name;

    const {formContents} = this.state;

    let value;
    if (event.target.type === 'checkbox') {
      value = event.target.checked;
    } else if (event.target.type === 'select-one') {
      value = event.target.value;
    } else {
      value = event.target.value;
    }

    formContents[fieldID] = value;

    this.setState({
      formContents: formContents,
    });
  }
  handleDelete() {
    const {formContents} = this.state;

    $.ajax({
      type: 'get',
      url: '/profile/view/delete?item=' + formContents.id,
      beforeSend: function prepSendDelete(xhr) {
        xhr.setRequestHeader('Accept', 'application/json');
      },
      success: () => {
        window.location.assign('/profile/view/');
      },
    });
  }
  handleCancel() {
    window.location.assign('/profile/view/');
  }
  handleSave() {
    const {formContents} = this.state;

    $.ajax({
      type: 'post',
      url: '/profile/api',
      data: formContents,
      beforeSend: function prepSendSave(xhr) {
        xhr.setRequestHeader('Accept', 'application/json');
      },
      success: (apiResponse) => {
        if (apiResponse.errors) {
          this.setState({
            apiResponse: apiResponse,
          });
        } else {
          window.location.assign('/profile/view/');
        }
      },
    });
  }
  processForm(apiResponse) {
    if (apiResponse) {
      // TODO This could be abstracted further for reuse throughout all
      // React / Django forms
      const profileUnits = apiResponse.ordered_fields.map( (profileUnitName, index) => {
        const profileUnit = apiResponse.fields[profileUnitName];
        function wrap(child) {
          return (
            <FieldWrapper
              label={profileUnit.label}
              helpText={profileUnit.help_text}
              errors={apiResponse.errors[profileUnitName]}
              required={profileUnit.required}
              key={index}>

              {child}

            </FieldWrapper>
          );
        }
        switch (profileUnit.widget.input_type) {
        case 'text':
          return wrap(
            <TextField
              name={profileUnitName}
              onChange={e => this.onChange(e, this)}
              required={profileUnit.required}
              initial={profileUnit.initial}
              maxLength={profileUnit.widget.maxlength}
              isHidden={profileUnit.widget.is_hidden}
              placeholder={profileUnit.widget.attrs.placeholder}
              />
          );
        case 'textarea':
          return wrap(
            <Textarea
              name={profileUnitName}
              onChange={e => this.onChange(e, this)}
              required={profileUnit.required}
              initial={profileUnit.initial}
              maxLength={profileUnit.widget.maxlength}
              isHidden={profileUnit.widget.is_hidden}
              placeholder={profileUnit.widget.attrs.placeholder}
              />
          );
        case 'date':
          return wrap(
            <Datetime
              name={profileUnitName}
              onChange={e => this.onChange(e, this)}
              required={profileUnit.required}
              initial={profileUnit.initial}
              maxLength={profileUnit.widget.maxlength}
              isHidden={profileUnit.widget.is_hidden}
              placeholder={profileUnit.widget.attrs.placeholder}
              />
          );
        case 'select':
          const initial = find(profileUnit.choices, function findValueOfInitialItem(c) {return c.value === profileUnit.initial;});
          return wrap(
            <Select
              name={profileUnitName}
              onChange={e => this.onChange(e, this)}
              initial={initial}
              choices={profileUnit.choices}
              />
          );
        case 'checkbox':
          return wrap(
            <CheckBox
              name={profileUnitName}
              onChange={e => this.onChange(e, this)}
              required={profileUnit.required}
              initial={profileUnit.initial}
              maxLength={profileUnit.widget.maxlength}
              isHidden={profileUnit.widget.is_hidden}
              placeholder={profileUnit.widget.attrs.placeholder}
              />
          );
        default:
        }
      });
      return profileUnits;
    }
  }
  callAPI() {
    const {formContents} = this.state;

    $.ajax({
      type: 'get',
      url: '/profile/api',
      data: {id: formContents.id,
             module: formContents.module},
      beforeSend: function prepSendCallAPI(xhr) {
        xhr.setRequestHeader('Accept', 'application/json');
      },
      success: (apiResponse) => {
        // Add form fields to state object
        for (const field in apiResponse.data) {
          if (apiResponse.data.hasOwnProperty(field)) {
            formContents[field] = apiResponse.data[field];
            // Replace null values with empty strings
            if (!formContents[field]) {
              formContents[field] = '';
            }
          }
        }
        this.setState({
          apiResponse: apiResponse,
          formContents: formContents,
        });
      },
    });
  }
  render() {
    const {formContents, apiResponse} = this.state;
    const moduleName = formContents.module;
    const processedFormComponents = this.processForm(apiResponse);

    return (
      <div>
        <div className="row">
          <div className="col-sm-12">
            <h1>Edit <small>{moduleName}</small></h1>
          </div>
        </div>
        <form action="" method="post" id="profile-unit-form" _lpchecked="1">
          {processedFormComponents}
          <div className="actions row">
            <div className="col-xs-12 col-md-offset-4 col-md-8 text-center">
              <a
                className="button"
                id="delete"
                onClick={e => this.handleDelete(e, this)}>
                Delete
              </a>
              <a
                href="/profile/view/"
                className="button"
                onClick={e => this.handleCancel(e, this)}>
                Cancel
              </a>
              <a
                className="button primary"
                id="profile-save"
                onClick={e => this.handleSave(e, this)}>
                Save
              </a>
            </div>
          </div>
        </form>
        <div className="clearfix"></div>
      </div>
    );
  }
}

Module.propTypes = {
  location: React.PropTypes.shape({
    query: React.PropTypes.shape({
      module: React.PropTypes.string.isRequired,
    }),
  }).isRequired,
  params: React.PropTypes.shape({
    moduleId: React.PropTypes.string,
  }).isRequired,
};

Module.defaultProps = {
  params: {},
};

render((
  <Router>
    <Route path="/" component={Module}>
      <IndexRoute component={Module} />
      <Route path="/:moduleId" component={Module} />
      <Route path="*" component={Module}/>
    </Route>
  </Router>
), document.getElementById('content'));

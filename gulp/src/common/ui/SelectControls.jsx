import React, {PropTypes} from 'react';
import warning from 'warning';
import {indexBy} from 'lodash-compat/collection';
import Select from 'common/ui/Select';


/**
 * Generic select dropdown which shows different vdom based on which item
 * is currently selected.
 *
 * example, currently set to choice '1':
 *
 *  <SelectControls
 *    choices={[
 *      {value: 1, display: 'Choose A content', render: () => <div>A</div>},
 *      {value: 2, display: 'Choose B content', render: () => <div>B</div>},
 *    ]}
 *    value={1}
 *    onSelect={value => ...}/>
 *
 * Note that value does not have to be a sequence of numbers. The order of
 * choices decides the order of the menu. Value can be any type that can be
 * tested for equality.
 */
export default function SelectControls(props) {
  const {choices, value, onSelect, loading, decoration} = props;

  const choiceIndex = indexBy(choices, c => c.value);

  warning(choiceIndex.hasOwnProperty(value),
    'SelectControls missing choice for ' + value);

  const {display, render: renderInner} = choiceIndex[value];


  let selectContents;
  if (loading) {
    selectContents = (
      <span>
        <span className="counter">
          <span className="report-loader"></span>
        </span>
        {display}
      </span>
    );
  } else if (decoration) {
    selectContents = (
      <span>
        <span className="counter">
          {decoration}
        </span>
        {display}
      </span>
    );
  } else {
    selectContents = display;
  }

  return (
    <div>
      <Select
        name=""
        onChange={v => onSelect(v.target.value)}
        value={selectContents}
        choices={choices}
        disable={loading}
      />
      <div className="select-control-chosen">
        {renderInner()}
      </div>
    </div>
  );
}

SelectControls.propTypes = {
  /**
   * Choices to display
   */
  choices: PropTypes.arrayOf(
    PropTypes.shape({
      /**
       * activate this choice when component value prop equals this;
       * should be a string or integer
       */
      value: PropTypes.any.isRequired,

      /**
       * string to display when active
       */
      display: PropTypes.string.isRequired,

      /**
       * function returning vdom called when this entry is active
       */
      render: PropTypes.func.isRequired,
    }).isRequired,
  ).isRequired,

  /**
   * Currently selected choice, must correspond to a value in choices.
   */
  value: PropTypes.any.isRequired,

  /**
   * Function to call if the user makes a new selection.
   */
  onSelect: PropTypes.func.isRequired,

  /**
   * disable this control while we load?
   */
  loading: PropTypes.bool,

  /**
   * text to show along with the displayed value in the main select
   */
  decoration: PropTypes.string,
};

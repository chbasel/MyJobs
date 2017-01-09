import React, {PropTypes} from 'react';
import {map} from 'lodash-compat/collection';
import TagSelect from './TagSelect';

/**
 * Control for and/or groups of tags.
 */
export default function TagAnd(props) {
  const {selected, available, onChoose, onRemove, placeholder} = props;

  const selectedPlusBlank = [...selected, []];
  return (
    <div className="tag-select-outer">
      {map(selectedPlusBlank, (ts, i) => (
        <div className="tag-select-first-input" key={i}>
          { i === 0
            ? <label>Include any of these tags</label>
            : <label><b>AND</b> any of these tags</label>}
          <TagSelect
            selected={ts}
            available={available}
            onChoose={v => onChoose(i, v)}
            onRemove={v => onRemove(i, v)}
            placeholder={placeholder}/>
        </div>
      ))}
    </div>
  );
}

TagAnd.propTypes = {
  /**
   * Array of Arrays of selected tags.
   */
  selected: PropTypes.arrayOf(
    PropTypes.arrayOf(
      PropTypes.shape({
        value: PropTypes.any.isRequired,
        display: PropTypes.string.isRequired,
        hexColor: PropTypes.string,
      })
    ).isRequired
  ).isRequired,
  /**
   * Array of available tags, shared by all tag selects.
   */
  available: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.any.isRequired,
      display: PropTypes.string.isRequired,
      hexColor: PropTypes.string,
    })
  ).isRequired,
  /**
   * Function called when an available tag is selected.
   */
  onChoose: PropTypes.func.isRequired,
  /**
   * Function called when a selected tag is removed.
   */
  onRemove: PropTypes.func.isRequired,
  /**
   * Show this text in blank tag selects
   */
  placeholder: PropTypes.string,
};


TagAnd.defaultProps = {
  placeholder: 'Not specified',
};

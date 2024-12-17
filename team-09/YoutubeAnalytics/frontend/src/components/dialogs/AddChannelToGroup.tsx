import { useState } from "react";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import { observer } from "mobx-react-lite";
import { Form } from "react-bootstrap";

interface Props {
  show: boolean;
  onChangeShowState: (state: boolean) => void;
  onAddToGroup: (customUrl: string) => void;
}

const AddChannelToGroup: React.FC<Props> = (props: Props) => {
  const [url, setUrl] = useState("");

  const onClose = () => {
    setUrl("");
    props.onChangeShowState(false);
  };

  const handleAddToGroup = () => {
    if (url === "") return;

    props.onAddToGroup(url);

    onClose();
  };

  return (
    <Modal show={props.show} onHide={onClose}>
      <Modal.Header closeButton>
        <Modal.Title>Добавить канал в группу</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form.Group>
          <Form.Label>Введите url:</Form.Label>
          <Form.Control
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            type="text"
            placeholder="url канала"
          />
        </Form.Group>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleAddToGroup}>
          Добавить
        </Button>
        <Button variant="primary" onClick={onClose}>
          Отмена
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default observer(AddChannelToGroup);

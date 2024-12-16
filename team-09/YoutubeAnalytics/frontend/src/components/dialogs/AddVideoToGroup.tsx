import { useState } from "react";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import { observer } from "mobx-react-lite";
import { Form } from "react-bootstrap";

interface Props {
  show: boolean;
  onChangeShowState: (state: boolean) => void;
  onAddToGroup: (videoId: string) => void;
}

const AddVideoToGroup: React.FC<Props> = (props: Props) => {
  const [url, setUrl] = useState("");

  const onClose = () => {
    setUrl("");
    props.onChangeShowState(false);
  };

  const handleAddToGroup = () => {
    const reg =
      "(?:https?:\\/\\/)?(?:www\\.)?(?:youtube\\.com\\/(?:[^\\/\\n\\s]+\\/\\S+\\/|(?:v|e(?:mbed)?)\\/|\\S*?[?&]v=)|youtu\\.be\\/)([a-zA-Z0-9_-]{11})";
    const matches = url.match(reg);
    if (!matches || matches.length < 2) return;

    props.onAddToGroup(matches[1]);

    onClose();
  };

  return (
    <Modal show={props.show} onHide={onClose}>
      <Modal.Header closeButton>
        <Modal.Title>Добавить видео в группу</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form.Group>
          <Form.Label>Введите url:</Form.Label>
          <Form.Control
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            type="text"
            placeholder="url видео"
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

export default observer(AddVideoToGroup);

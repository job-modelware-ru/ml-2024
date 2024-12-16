import { observer } from "mobx-react-lite";
import { useState, useContext, useEffect } from "react";
import { Context } from "..";
import { useParams } from "react-router-dom";
import $api from "../http";
import { AuthResponse } from "../models/response/AuthResponse";
import { Col, Row, Button } from "react-bootstrap";

interface Props {
  yt_id: string | undefined;
  emotion_id: number;
}

interface Comment {
  id: number;
  yt_id: string;
  original_text: string;
  author_display_name: string;
  like_count: number;
  published_at: string;
  updated_at: string;
  total_reply_count: number;
  emotion: number;
  video: string;
  replies: [];
}

interface CommentsData {
  count: number;
  next: string;
  previous: string;
  results: Comment[];
}

const Comments: React.FC<Props> = (props: Props) => {
  const { store } = useContext(Context);
  const [commentsData, setCommentsData] = useState<CommentsData>();

  const fetchPlotData = async (page: string | undefined) => {
    try {
      // const url = "comment/?video_id=${props.yt_id}";
      var response;
      if (!page)
        response = await $api.get<AuthResponse>("comment/", {
          params: { video_id: props.yt_id, emotion_id: props.emotion_id },
        });
      else {
        page = "https" + page.slice(4);
        response = await $api.get<AuthResponse>(page);
      }

      // setCommentsData(response.data as unknown as CommentsData);
      setCommentsData(response.data as unknown as CommentsData);
    } catch (error) {
      console.error("Error fetching plot data:", error);
    }
  };

  useEffect(() => {
    fetchPlotData(undefined);
  }, []);

  const generateComments = () => {
    if (!commentsData) return null;

    return commentsData?.results.map((data) => {
      return (
        <div>
          <ul>
            <li key={data.id}>{data.original_text}</li>
          </ul>
        </div>
      );
    });
  };

  const emotion_labels = [
    "sadness",
    "joy",
    "love",
    "anger",
    "fear",
    "surprise",
    "neutral",
  ];

  return (
    <div>
      <Button
        variant="primary"
        onClick={() => fetchPlotData(commentsData?.previous)}
      >
        Пред
      </Button>
      <Button
        variant="primary"
        onClick={() => fetchPlotData(commentsData?.next)}
      >
        След
      </Button>
      <h1>{emotion_labels[props.emotion_id - 1]}</h1>
      <div>{generateComments()}</div>
    </div>
  );
};

export default observer(Comments);

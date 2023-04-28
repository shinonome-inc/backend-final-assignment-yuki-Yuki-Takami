const getCookie = (name) => {
  if (document.cookie && document.cookie !== '') {
    for (const cookie of document.cookie.split(';')) {
      const [key, value] = cookie.trim().split('=');
      if (key === name) {
        return decodeURIComponent(value);
      }
    }
  }
};
const csrftoken = getCookie('csrftoken');


const like = async (tweet) => {
  const url = tweet.dataset.url;
  console.log(tweet)
  const data = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
  }
  const response = await fetch(url, data);
  const tweet_data = await response.json();
  changeStyle(tweet_data, tweet);
}

const changeStyle = (tweet_data, selector) => {
  const count = document.querySelector(`#count_${tweet_data.tweet_id}`)
  console.log(count)

  if (tweet_data.is_liked) {
    unlike_url = `/tweets/${tweet_data.tweet_id}/unlike/`
    selector.setAttribute('data-url', unlike_url);
    selector.innerHTML = "いいね解除";
    console.log(tweet_data.liked_count)
    count.innerHTML = `いいね数 ${tweet_data.liked_count}`;
  } else {
    like_url = `/tweets/${tweet_data.tweet_id}/like/`
    selector.setAttribute('data-url', like_url);
    selector.innerHTML = "いいね";
    count.innerHTML = `いいね数 ${tweet_data.liked_count}`;
  }
}

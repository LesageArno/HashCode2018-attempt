#include <cstdio>
#include <iostream>
#include <vector>

using namespace std;

typedef struct ride
{
  int start_x;
  int start_y;
  int finish_x;
  int finish_y;
  int earliest_start;
  int latest_finish;
  int finished;
} rides;

int distance(int x, int y, int a, int b)
{
  return (abs(y - b) + abs(x - a));
}

int main(int argc, char *argv[])
{
  if (argc < 3)
  {
    cout << "USAGE: ./judge input output" << endl
         << "With:" << endl;
    cout << "  - input: the filename in which there is the instance," << endl;
    cout << "  - output: the filename in which there is the solution." << endl;
    cout << "example: ./judge testcases/a_example.txt testcases/a_example.out" << endl;
    exit(0);
  }

  FILE *input = fopen(argv[1], "r");
  if (input == NULL)
  {
    cout << "Cannot open file " << argv[1] << endl;
    exit(0);
  }

  FILE *output = fopen(argv[2], "r");
  if (output == NULL)
  {
    cout << "Cannot open file " << argv[2] << endl;
    exit(0);
  }

  /* Parse data file */
  int R, C, F, N, B, T;
  fscanf(input, "%d %d %d %d %d %d", &R, &C, &F, &N, &B, &T);

  vector<ride> rides(N);
  for (int i = 0; i < N; i++)
  {
    int tmp;
    fscanf(input, "%d", &tmp);
    rides[i].start_x = tmp;
    fscanf(input, "%d", &tmp);
    rides[i].start_y = tmp;
    fscanf(input, "%d", &tmp);
    rides[i].finish_x = tmp;
    fscanf(input, "%d", &tmp);
    rides[i].finish_y = tmp;
    fscanf(input, "%d", &tmp);
    rides[i].earliest_start = tmp;
    fscanf(input, "%d", &tmp);
    rides[i].latest_finish = tmp;
    rides[i].finished = 0;
  }
  /* End parsing data file */

  /* Parse and check solution */
  int nbRIdes = 0;
  vector<int> solutions[F];
  for (int i = 0; i < F; i++)
  {
    int M, nextNb;
    fscanf(output, "%d", &M);
    for (int j = 0; j < M; j++)
    {
      fscanf(output, "%d", &nextNb);
      if (nextNb < 0 || nextNb >= N)
      {
        cout << "There is no ride number " << nextNb << "." << endl;
        return 0;
      }
      if (rides[nextNb].finished)
      {
        cout << "Ride number " << nextNb << " is already assigned." << endl;
        return 0;
      }
      rides[nextNb].finished = 1;
      solutions[i].push_back(nextNb);
    }
    nbRIdes += M;
  }
  if (nbRIdes > N)
  {
    cout << "Too much rides assigned." << endl;
    return 0;
  }
  /* End parsing solution */

  /* Compute score */
  vector<long long> carScore(F);
  for (int i = 0; i < F; i++)
  {
    carScore[i] = 0;
  }

  for (int i = 0; i < F; i++)
  {
    vector<int> sol = solutions[i];
    int last_pos_x = 0;
    int last_pos_y = 0;
    int currentTime = 0;
    for (int j = 0; j < sol.size(); j++)
    {
      ride r = rides[sol[j]];
      int dist2start = distance(r.start_x, r.start_y, last_pos_x, last_pos_y);
      int start = dist2start + currentTime;
      int bonus = 0;
      if (start <= r.earliest_start)
      {
        start = r.earliest_start;
        bonus = B;
      }
      int dist2dest = distance(r.start_x, r.start_y, r.finish_x, r.finish_y);

      if (start + dist2dest <= r.latest_finish)
      {
        carScore[i] += bonus + dist2dest;
        last_pos_x = r.finish_x;
        last_pos_y = r.finish_y;
        currentTime = start + dist2dest;
      }
    }
  }

  long long sum = 0;
  for (int i = 0; i < F; i++)
  {
    sum += carScore[i];
  }

  cout << "Score = " << sum << endl;
  return 0;
}
